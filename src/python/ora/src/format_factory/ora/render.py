"""ORA-RENDER-001 / ORA-COMPOSITE-001 / ORA-ISOLATION-001 / ORA-STREAM-001 /
ORA-BASELINEASSET-001 -- pixel-level rendering.

Every other module in this package answers "what does the document say";
this module is the one that answers "what does it look like": decode each
referenced layer's PNG raster, composite the layer stack deterministically
per the Layer Stack Specification's own compositing model, and produce a
single merged RGBA image. Nothing else in the package does this -- the
"render" name that appears in ``lifecycle.py`` is an unrelated XML
serialization helper, and ``composite_ops.py`` only looks up a composite-op
value's *declared meaning*; it performs no pixel arithmetic.

Grounding for the compositing model, quoted from the pinned Layer Stack
Specification (``.local/format-contracts/acquired/ora/src-ora-003.bin``):

    "For a non-root stack, x and y are ignored. They do not add an offset
    to the layers contained in the stack. ... The offset of the contained
    layers is solely defined by their own x and y attributes."

    "Layer stacks should be composited in a manner conforming to the W3C's
    Compositing and Blending Level 1 Candidate Recommendation."

    "Isolated groups are always rendered independently at first, starting
    with a fully-transparent 'black' backdrop (rgba={0,0,0,0}). The results
    of this independent composite are then rendered on top of the group's
    own backdrop using the group's opacity and composite mode settings.
    Conversely non-isolated groups are rendered by rendering each child
    layer or sub-stack in turn to the group's backdrop, just as if there
    were no stacked group."

    "The root stack has a fixed, implicit rendering in OpenRaster: it is to
    composite as an isolated group over a background of the application's
    choice." -- this library's own choice is fully transparent, matching
    the format's own mandatory merged-image asset (itself an RGBA PNG).

``OraStack.is_isolated_group`` (model/stack.py) already implements the
"isolated when isolation is isolate, opacity is below one, or composite-op
differs from svg:src-over" rule this module relies on; it is not
reimplemented here.

Deliberately out of scope, and not claimed: Adam7-interlaced layer
rasters (refused, not mis-decoded); ``<text>`` elements (this package's
baseline reading profile does not interpret text -- see ``OraText``); any
notion of "mask" (ORA-MASK-001 was independently investigated and found
unsupported by the pinned spec sources, so nothing here invents one); and
cross-producer golden-image interoperability proof, which needs an
acquired independent corpus this session does not have.
"""

from __future__ import annotations

import struct
import zlib
from array import array
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from typing import Protocol

from format_factory.core import (
    DEFAULT_LIMITS,
    CheckedArithmeticError,
    ResourceLimits,
    checked_product,
)

from .codec.png_metadata import (
    COLOUR_TYPES,
    PNG_SIGNATURE,
    THUMBNAIL_MAX_EDGE,
    read_png_metadata,
)
from .errors import OraLimitError, OraValidationError
from .model.composite_ops import DEFAULT_COMPOSITE_OP, composite_op_info
from .model.document import OraDocument
from .model.stack import OraChild, OraLayer, OraStack, OraText

# ---------------------------------------------------------------------------
# PNG pixel codec -- decode/encode straight-alpha RGBA8, no pixel library
# dependency (this package has none), matching png_metadata.py's own
# stdlib-only, bounded-reader style.
# ---------------------------------------------------------------------------

_FILTER_NONE = 0
_FILTER_SUB = 1
_FILTER_UP = 2
_FILTER_AVERAGE = 3
_FILTER_PAETH = 4


@dataclass(frozen=True)
class DecodedRaster:
    """A decoded or rendered image: straight-alpha RGBA8, row-major,
    4 bytes per pixel. Used both for one decoded layer and for a
    composited (rendered) result -- the two have the same shape."""

    width: int
    height: int
    pixels: bytes


def _paeth(a: int, b: int, c: int) -> int:
    """PNG's Paeth predictor (a=left, b=above, c=upper-left)."""
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _iter_chunks(payload: bytes) -> Iterator[tuple[bytes, bytes]]:
    """Yield (type, data) for every chunk after the signature, verifying
    each chunk's CRC. A corrupt or truncated chunk is a validation error,
    not a crash -- this is a bounded reader over a stranger's bytes."""
    offset = len(PNG_SIGNATURE)
    total = len(payload)
    while offset < total:
        if offset + 8 > total:
            raise OraValidationError("asset is truncated inside a PNG chunk header")
        length, kind = struct.unpack(">I4s", payload[offset : offset + 8])
        data_start = offset + 8
        data_end = data_start + length
        if data_end + 4 > total:
            raise OraValidationError(
                f"asset is truncated inside a {kind.decode('ascii', 'replace')!r} chunk"
            )
        data = payload[data_start:data_end]
        (crc,) = struct.unpack(">I", payload[data_end : data_end + 4])
        if (zlib.crc32(payload[offset + 4 : data_end]) & 0xFFFFFFFF) != crc:
            raise OraValidationError(
                f"asset has a corrupt {kind.decode('ascii', 'replace')!r} chunk: CRC mismatch"
            )
        yield kind, data
        offset = data_end + 4
        if kind == b"IEND":
            break


def _checked(values: tuple[int, ...], *, ceiling: int, label: str) -> int:
    try:
        return checked_product(values, ceiling=ceiling, label=label)
    except CheckedArithmeticError as exc:
        raise OraLimitError(str(exc)) from exc


def decode_png(payload: bytes, *, limits: ResourceLimits = DEFAULT_LIMITS) -> DecodedRaster:
    """Decode a non-interlaced PNG to straight-alpha RGBA8 pixels.

    Colour types 0 (greyscale), 2 (truecolour), 3 (indexed, via PLTE/tRNS),
    4 (greyscale+alpha) and 6 (truecolour+alpha) are supported at every bit
    depth PNG permits for that type. Interlaced (Adam7) input is refused
    rather than silently mis-decoded -- a disclosed scope boundary.

    `read_png_metadata` (ORA-ASSET-001) already bounds the declared raster
    size against `limits` before a single byte is inflated; calling it here
    keeps that guarantee independent of caller order, and the decompressor
    below is additionally capped to the exact expected scanline-buffer size
    computed from that same declaration, so a hostile IDAT stream cannot
    inflate past what the header promised.
    """
    metadata = read_png_metadata(payload, limits=limits)
    if metadata.interlaced:
        raise OraValidationError(
            "asset uses Adam7 interlacing, which this renderer does not decode"
        )

    channels, _ = COLOUR_TYPES[metadata.colour_type]
    bits_per_pixel = channels * metadata.bit_depth
    bytes_per_scanline = (bits_per_pixel * metadata.width + 7) // 8
    filter_bpp = max(1, (bits_per_pixel + 7) // 8)

    expected_raw = _checked(
        (metadata.height, bytes_per_scanline + 1),
        ceiling=limits.max_decompressed_bytes,
        label="ORA layer scanline buffer",
    )

    palette: bytes | None = None
    trns: bytes | None = None
    idat_parts: list[bytes] = []
    for kind, data in _iter_chunks(payload):
        if kind == b"PLTE":
            palette = data
        elif kind == b"tRNS":
            trns = data
        elif kind == b"IDAT":
            idat_parts.append(data)

    if metadata.colour_type == 3 and palette is None:
        raise OraValidationError("asset is indexed-colour but has no PLTE chunk")

    decompressor = zlib.decompressobj()
    raw = bytearray()
    for chunk in idat_parts:
        remaining = expected_raw - len(raw)
        if remaining <= 0:
            break
        raw.extend(decompressor.decompress(chunk, remaining))
    if 0 < len(raw) < expected_raw:
        raw.extend(decompressor.decompress(b"", expected_raw - len(raw)))
    if len(raw) != expected_raw:
        raise OraValidationError(
            f"asset's decompressed scanline data is {len(raw)} bytes, expected "
            f"exactly {expected_raw} for {metadata.width}x{metadata.height} at "
            f"{metadata.bit_depth}-bit colour type {metadata.colour_type}"
        )

    unfiltered = bytearray(metadata.height * bytes_per_scanline)
    prev = bytes(bytes_per_scanline)
    pos = 0
    for row in range(metadata.height):
        filter_type = raw[pos]
        pos += 1
        line = bytearray(raw[pos : pos + bytes_per_scanline])
        pos += bytes_per_scanline
        if filter_type == _FILTER_NONE:
            pass
        elif filter_type == _FILTER_SUB:
            for i in range(filter_bpp, bytes_per_scanline):
                line[i] = (line[i] + line[i - filter_bpp]) & 0xFF
        elif filter_type == _FILTER_UP:
            for i in range(bytes_per_scanline):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif filter_type == _FILTER_AVERAGE:
            for i in range(bytes_per_scanline):
                a = line[i - filter_bpp] if i >= filter_bpp else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 0xFF
        elif filter_type == _FILTER_PAETH:
            for i in range(bytes_per_scanline):
                a = line[i - filter_bpp] if i >= filter_bpp else 0
                b = prev[i]
                c = prev[i - filter_bpp] if i >= filter_bpp else 0
                line[i] = (line[i] + _paeth(a, b, c)) & 0xFF
        else:
            raise OraValidationError(f"asset uses unknown PNG filter type {filter_type}")
        start = row * bytes_per_scanline
        unfiltered[start : start + bytes_per_scanline] = line
        prev = bytes(line)

    pixels = _samples_to_rgba8(
        bytes(unfiltered),
        width=metadata.width,
        height=metadata.height,
        bit_depth=metadata.bit_depth,
        colour_type=metadata.colour_type,
        palette=palette,
        trns=trns,
    )
    return DecodedRaster(width=metadata.width, height=metadata.height, pixels=pixels)


def _sample_at(line: bytes, index: int, bit_depth: int) -> int:
    """The `index`-th `bit_depth`-bit sample in `line` (MSB-first packing
    for sub-byte depths, per the PNG spec)."""
    if bit_depth == 8:
        return line[index]
    if bit_depth == 16:
        o = index * 2
        return (line[o] << 8) | line[o + 1]
    bit_offset = index * bit_depth
    byte_index = bit_offset // 8
    shift = 8 - bit_depth - (bit_offset % 8)
    mask = (1 << bit_depth) - 1
    return (line[byte_index] >> shift) & mask


def _samples_to_rgba8(
    unfiltered: bytes,
    *,
    width: int,
    height: int,
    bit_depth: int,
    colour_type: int,
    palette: bytes | None,
    trns: bytes | None,
) -> bytes:
    channels, _ = COLOUR_TYPES[colour_type]
    bits_per_pixel = channels * bit_depth
    bytes_per_scanline = (bits_per_pixel * width + 7) // 8
    out = bytearray(width * height * 4)

    max_sample = (1 << bit_depth) - 1
    scale8 = 255.0 / max_sample if max_sample else 0.0

    trns_grey: int | None = None
    trns_rgb: tuple[int, int, int] | None = None
    trns_alpha: bytes = b""
    if trns is not None:
        if colour_type == 0:
            (trns_grey,) = struct.unpack(">H", (trns + b"\x00\x00")[:2])
        elif colour_type == 2:
            trns_rgb = struct.unpack(">HHH", (trns + b"\x00" * 6)[:6])
        elif colour_type == 3:
            trns_alpha = trns

    for y in range(height):
        line = unfiltered[y * bytes_per_scanline : (y + 1) * bytes_per_scanline]
        row_out = y * width * 4
        for x in range(width):
            base = x * channels
            o = row_out + x * 4
            if colour_type == 0:
                g = _sample_at(line, base, bit_depth)
                v = round(g * scale8)
                a = 0 if trns_grey is not None and g == trns_grey else 255
                out[o], out[o + 1], out[o + 2], out[o + 3] = v, v, v, a
            elif colour_type == 2:
                r = _sample_at(line, base, bit_depth)
                g = _sample_at(line, base + 1, bit_depth)
                b = _sample_at(line, base + 2, bit_depth)
                a = 0 if trns_rgb is not None and (r, g, b) == trns_rgb else 255
                out[o] = round(r * scale8)
                out[o + 1] = round(g * scale8)
                out[o + 2] = round(b * scale8)
                out[o + 3] = a
            elif colour_type == 3:
                idx = _sample_at(line, base, bit_depth)
                if palette is None or idx * 3 + 3 > len(palette):
                    raise OraValidationError(
                        f"asset references palette index {idx} outside PLTE"
                    )
                out[o] = palette[idx * 3]
                out[o + 1] = palette[idx * 3 + 1]
                out[o + 2] = palette[idx * 3 + 2]
                out[o + 3] = trns_alpha[idx] if idx < len(trns_alpha) else 255
            elif colour_type == 4:
                g = _sample_at(line, base, bit_depth)
                a = _sample_at(line, base + 1, bit_depth)
                v = round(g * scale8)
                out[o] = out[o + 1] = out[o + 2] = v
                out[o + 3] = round(a * scale8)
            else:  # 6: truecolour + alpha
                r = _sample_at(line, base, bit_depth)
                g = _sample_at(line, base + 1, bit_depth)
                b = _sample_at(line, base + 2, bit_depth)
                a = _sample_at(line, base + 3, bit_depth)
                out[o] = round(r * scale8)
                out[o + 1] = round(g * scale8)
                out[o + 2] = round(b * scale8)
                out[o + 3] = round(a * scale8)
    return bytes(out)


_TRUECOLOUR_ALPHA = 6


def encode_png(raster: DecodedRaster) -> bytes:
    """Encode straight-alpha RGBA8 pixels as a conforming 8-bit
    truecolour-with-alpha PNG: non-interlaced, filter type None on every
    scanline. Determinism over compression ratio -- the same pixels always
    produce the same bytes, matching this package's write-path ethos
    (see lifecycle.py's module docstring: "Determinism by construction")."""
    if raster.width <= 0 or raster.height <= 0:
        raise OraValidationError("cannot encode a PNG with a non-positive dimension")

    ihdr = struct.pack(
        ">IIBBBBB", raster.width, raster.height, 8, _TRUECOLOUR_ALPHA, 0, 0, 0
    )
    bytes_per_scanline = raster.width * 4
    raw = bytearray()
    for y in range(raster.height):
        raw.append(_FILTER_NONE)
        row_start = y * bytes_per_scanline
        raw.extend(raster.pixels[row_start : row_start + bytes_per_scanline])
    idat = zlib.compress(bytes(raw), 9)

    parts = [PNG_SIGNATURE]
    for kind, data in ((b"IHDR", ihdr), (b"IDAT", idat), (b"IEND", b"")):
        parts.append(struct.pack(">I", len(data)))
        parts.append(kind)
        parts.append(data)
        parts.append(struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))
    return b"".join(parts)


def _box_downscale(raster: DecodedRaster, new_width: int, new_height: int) -> DecodedRaster:
    out = bytearray(new_width * new_height * 4)
    for ny in range(new_height):
        y0 = ny * raster.height // new_height
        y1 = max(y0 + 1, (ny + 1) * raster.height // new_height)
        for nx in range(new_width):
            x0 = nx * raster.width // new_width
            x1 = max(x0 + 1, (nx + 1) * raster.width // new_width)
            r_sum = g_sum = b_sum = a_sum = 0
            count = 0
            for sy in range(y0, y1):
                row = sy * raster.width * 4
                for sx in range(x0, x1):
                    o = row + sx * 4
                    r_sum += raster.pixels[o]
                    g_sum += raster.pixels[o + 1]
                    b_sum += raster.pixels[o + 2]
                    a_sum += raster.pixels[o + 3]
                    count += 1
            o = (ny * new_width + nx) * 4
            out[o] = round(r_sum / count)
            out[o + 1] = round(g_sum / count)
            out[o + 2] = round(b_sum / count)
            out[o + 3] = round(a_sum / count)
    return DecodedRaster(width=new_width, height=new_height, pixels=bytes(out))


def generate_thumbnail(
    raster: DecodedRaster, *, max_edge: int = THUMBNAIL_MAX_EDGE
) -> bytes:
    """Downscale `raster` to fit within `max_edge` x `max_edge` (the
    thumbnail's own conformance bound -- see
    `RasterMetadata.satisfies_thumbnail_constraints`) using box-average
    downsampling, and encode the result as an 8-bit non-interlaced PNG. A
    raster already within bounds is encoded unchanged."""
    if raster.width <= max_edge and raster.height <= max_edge:
        return encode_png(raster)
    scale = min(max_edge / raster.width, max_edge / raster.height)
    new_width = max(1, round(raster.width * scale))
    new_height = max(1, round(raster.height * scale))
    return encode_png(_box_downscale(raster, new_width, new_height))


# ---------------------------------------------------------------------------
# Compositing -- W3C Compositing and Blending Level 1 formulas, using the
# blend function / Porter-Duff operator pairs already catalogued in
# model/composite_ops.py's COMPOSITE_OP_REGISTRY.
# ---------------------------------------------------------------------------

_RGB = tuple[float, float, float]


def _multiply(cb: float, cs: float) -> float:
    return cb * cs


def _screen(cb: float, cs: float) -> float:
    return cb + cs - cb * cs


def _hard_light(cb: float, cs: float) -> float:
    return _multiply(cb, 2 * cs) if cs <= 0.5 else _screen(cb, 2 * cs - 1)


def _overlay(cb: float, cs: float) -> float:
    return _hard_light(cs, cb)


def _color_dodge(cb: float, cs: float) -> float:
    if cb == 0.0:
        return 0.0
    if cs >= 1.0:
        return 1.0
    return min(1.0, cb / (1.0 - cs))


def _color_burn(cb: float, cs: float) -> float:
    if cb >= 1.0:
        return 1.0
    if cs <= 0.0:
        return 0.0
    return 1.0 - min(1.0, (1.0 - cb) / cs)


def _soft_light(cb: float, cs: float) -> float:
    if cs <= 0.5:
        return cb - (1 - 2 * cs) * cb * (1 - cb)
    d = ((16 * cb - 12) * cb + 4) * cb if cb <= 0.25 else cb**0.5
    return cb + (2 * cs - 1) * (d - cb)


_SEPARABLE_BLEND: dict[str, Callable[[float, float], float]] = {
    "Normal": lambda cb, cs: cs,
    "Multiply": _multiply,
    "Screen": _screen,
    "Overlay": _overlay,
    "Darken": min,
    "Lighten": max,
    "Color Dodge": _color_dodge,
    "Color Burn": _color_burn,
    "Hard Light": _hard_light,
    "Soft Light": _soft_light,
    "Difference": lambda cb, cs: abs(cb - cs),
}


def _lum(c: _RGB) -> float:
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def _clip_colour(c: _RGB) -> _RGB:
    r, g, b = c
    lum = _lum(c)
    lo = min(r, g, b)
    hi = max(r, g, b)
    if lo < 0.0 and lum != lo:
        scale = lum / (lum - lo)
        r = lum + (r - lum) * scale
        g = lum + (g - lum) * scale
        b = lum + (b - lum) * scale
    if hi > 1.0 and hi != lum:
        scale = (1.0 - lum) / (hi - lum)
        r = lum + (r - lum) * scale
        g = lum + (g - lum) * scale
        b = lum + (b - lum) * scale
    return (r, g, b)


def _set_lum(c: _RGB, lum: float) -> _RGB:
    d = lum - _lum(c)
    return _clip_colour((c[0] + d, c[1] + d, c[2] + d))


def _sat(c: _RGB) -> float:
    return max(c) - min(c)


def _set_sat(c: _RGB, s: float) -> _RGB:
    order = sorted(range(3), key=lambda i: c[i])
    lo, mid, hi = order
    out = [0.0, 0.0, 0.0]
    if c[hi] > c[lo]:
        out[mid] = (c[mid] - c[lo]) * s / (c[hi] - c[lo])
        out[hi] = s
    return (out[0], out[1], out[2])


def _blend_hue(cb: _RGB, cs: _RGB) -> _RGB:
    return _set_lum(_set_sat(cs, _sat(cb)), _lum(cb))


def _blend_saturation(cb: _RGB, cs: _RGB) -> _RGB:
    return _set_lum(_set_sat(cb, _sat(cs)), _lum(cb))


def _blend_color(cb: _RGB, cs: _RGB) -> _RGB:
    return _set_lum(cs, _lum(cb))


def _blend_luminosity(cb: _RGB, cs: _RGB) -> _RGB:
    return _set_lum(cb, _lum(cs))


_NONSEPARABLE_BLEND: dict[str, Callable[[_RGB, _RGB], _RGB]] = {
    "Hue": _blend_hue,
    "Saturation": _blend_saturation,
    "Color": _blend_color,
    "Luminosity": _blend_luminosity,
}

_SOURCE_OVER = "Source Over"


def _porter_duff_coeffs(operator: str, alpha_s: float, alpha_b: float) -> tuple[float, float]:
    """(Fa, Fb) coefficients such that Co = Fa*(alpha_s*Cs) + Fb*Cb_premult,
    per Porter & Duff (1984). Only the operators `COMPOSITE_OP_REGISTRY`
    actually names are supported."""
    if operator == _SOURCE_OVER:
        return 1.0, 1.0 - alpha_s
    if operator == "Lighter":
        return 1.0, 1.0
    if operator == "Destination In":
        return 0.0, alpha_s
    if operator == "Destination Out":
        return 0.0, 1.0 - alpha_s
    if operator == "Source Atop":
        return alpha_b, 1.0 - alpha_s
    if operator == "Destination Atop":
        return 1.0 - alpha_b, alpha_s
    raise OraValidationError(f"unsupported Porter-Duff compositing operator {operator!r}")


def _composite_layer_onto(
    canvas: "array[float]",
    canvas_width: int,
    canvas_height: int,
    raster_pixels: bytes,
    raster_width: int,
    raster_height: int,
    *,
    x: int,
    y: int,
    opacity: float,
    composite_op: str,
) -> None:
    """Alpha-composite one straight-alpha RGBA8 raster onto `canvas` (a
    premultiplied float32-per-channel buffer). `composite_op` selects the
    blend function and Porter-Duff operator via `composite_op_info`; an
    unrecognized (forward-compatible) value falls back to the default --
    rendering cannot invent semantics for a mode it does not know.

    For Source Over (every blend function pairs with it), only the overlap
    of the raster's placed bounds and the canvas is touched: outside that
    overlap alpha_s=0, and Source Over's own Fb=(1-alpha_s)=1 there, i.e.
    "leave the canvas exactly as it was" -- skipping those pixels is a
    genuine optimization, not an approximation.

    For the other 5 Porter-Duff operators this is NOT generally true --
    Destination In and Destination Atop both have Fb=alpha_s, which is 0.0
    (not 1.0) outside the source's own bounds, meaning the destination
    must be CLEARED there, not left untouched. (Confirmed via
    ORA-COMPOSITE-001's own full-inventory producer-verification sweep,
    2026-08-12: a from-scratch independent oracle caught this exact
    discrepancy; test_destination_in_clears_the_destination_outside_the_
    source_layers_own_bounds and its own Destination Atop sibling in
    test_obligation_render_and_compositing.py pin it down.) These 5
    operators are therefore evaluated over the FULL canvas, with
    out-of-bounds pixels treated as the true, explicit alpha_s=0 the
    Porter-Duff formula itself expects -- not skipped."""
    info = composite_op_info(composite_op) or composite_op_info(DEFAULT_COMPOSITE_OP)
    assert info is not None  # DEFAULT_COMPOSITE_OP is always in the registry
    blend_name = info.blending_function
    operator = info.compositing_operator
    is_source_over = operator == _SOURCE_OVER
    separable = _SEPARABLE_BLEND.get(blend_name) if is_source_over else None
    nonseparable = _NONSEPARABLE_BLEND.get(blend_name) if is_source_over else None

    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(canvas_width, x + raster_width), min(canvas_height, y + raster_height)

    if is_source_over:
        if x0 >= x1 or y0 >= y1:
            return
        cy_range: range = range(y0, y1)
        cx_range: range = range(x0, x1)
    else:
        cy_range = range(canvas_height)
        cx_range = range(canvas_width)

    for cy in cy_range:
        ry = cy - y
        canvas_row = cy * canvas_width * 4
        raster_row = ry * raster_width * 4
        in_y_bounds = y0 <= cy < y1
        for cx in cx_range:
            rx = cx - x
            if in_y_bounds and x0 <= cx < x1:
                o_src = raster_row + rx * 4
                alpha_s = (raster_pixels[o_src + 3] / 255.0) * opacity
                cs = (
                    raster_pixels[o_src] / 255.0,
                    raster_pixels[o_src + 1] / 255.0,
                    raster_pixels[o_src + 2] / 255.0,
                )
            else:
                alpha_s = 0.0
                cs = (0.0, 0.0, 0.0)

            ci = canvas_row + cx * 4
            rb, gb, bb, alpha_b = canvas[ci], canvas[ci + 1], canvas[ci + 2], canvas[ci + 3]

            if is_source_over:
                if blend_name == "Normal":
                    cm = cs
                elif nonseparable is not None:
                    cb = (rb / alpha_b, gb / alpha_b, bb / alpha_b) if alpha_b > 0.0 else (0.0, 0.0, 0.0)
                    cm = nonseparable(cb, cs)
                else:
                    fn = separable if separable is not None else (lambda a, b: b)
                    cb = (rb / alpha_b, gb / alpha_b, bb / alpha_b) if alpha_b > 0.0 else (0.0, 0.0, 0.0)
                    cm = (fn(cb[0], cs[0]), fn(cb[1], cs[1]), fn(cb[2], cs[2]))
                blended = (
                    (1 - alpha_b) * cs[0] + alpha_b * cm[0],
                    (1 - alpha_b) * cs[1] + alpha_b * cm[1],
                    (1 - alpha_b) * cs[2] + alpha_b * cm[2],
                )
                new_r = alpha_s * blended[0] + (1 - alpha_s) * rb
                new_g = alpha_s * blended[1] + (1 - alpha_s) * gb
                new_b = alpha_s * blended[2] + (1 - alpha_s) * bb
                new_a = alpha_s + alpha_b * (1 - alpha_s)
            else:
                fa, fb = _porter_duff_coeffs(operator, alpha_s, alpha_b)
                sr, sg, sb = alpha_s * cs[0], alpha_s * cs[1], alpha_s * cs[2]
                new_r = fa * sr + fb * rb
                new_g = fa * sg + fb * gb
                new_b = fa * sb + fb * bb
                new_a = fa * alpha_s + fb * alpha_b

            canvas[ci], canvas[ci + 1], canvas[ci + 2], canvas[ci + 3] = (
                new_r,
                new_g,
                new_b,
                new_a,
            )


def _new_transparent_canvas(width: int, height: int) -> "array[float]":
    return array("d", bytes(8 * width * height * 4))


def _clamp255(value: float) -> int:
    scaled = round(value * 255.0)
    return 0 if scaled < 0 else 255 if scaled > 255 else scaled


def _canvas_to_straight_rgba8(canvas: "array[float]", width: int, height: int) -> bytes:
    out = bytearray(width * height * 4)
    for i in range(width * height):
        o = i * 4
        r, g, b, a = canvas[o], canvas[o + 1], canvas[o + 2], canvas[o + 3]
        if a > 0.0:
            r, g, b = r / a, g / a, b / a
        out[o] = _clamp255(r)
        out[o + 1] = _clamp255(g)
        out[o + 2] = _clamp255(b)
        out[o + 3] = _clamp255(a)
    return bytes(out)


def _resolve_member(members: Mapping[str, bytes], src: str) -> bytes:
    if src not in members:
        raise OraValidationError(
            f"layer references {src!r}, which is not an archive member"
        )
    return members[src]


def _render_children(
    children: tuple[OraChild, ...],
    canvas: "array[float]",
    *,
    width: int,
    height: int,
    resolve: Callable[[str], bytes],
    limits: ResourceLimits,
) -> None:
    # "its first child is the uppermost item in visual layer order"
    # (model/stack.py) -- painting bottom-to-top means walking in reverse.
    for child in reversed(children):
        _render_node(child, canvas, width=width, height=height, resolve=resolve, limits=limits)


def _render_node(
    node: OraChild,
    canvas: "array[float]",
    *,
    width: int,
    height: int,
    resolve: Callable[[str], bytes],
    limits: ResourceLimits,
) -> None:
    if not node.is_visible:
        return
    if isinstance(node, OraText):
        return  # no interpretable raster; see model/stack.py's OraText
    if isinstance(node, OraLayer):
        raster = decode_png(resolve(node.src), limits=limits)
        _composite_layer_onto(
            canvas,
            width,
            height,
            raster.pixels,
            raster.width,
            raster.height,
            x=node.x,
            y=node.y,
            opacity=node.opacity,
            composite_op=node.composite_op,
        )
        return
    # OraStack
    if node.is_isolated_group:
        sub_canvas = _new_transparent_canvas(width, height)
        _render_children(
            node.children, sub_canvas, width=width, height=height, resolve=resolve, limits=limits
        )
        sub_pixels = _canvas_to_straight_rgba8(sub_canvas, width, height)
        # Stack x/y are never applied (see module docstring); the isolated
        # result is already canvas-sized and placed at the origin.
        _composite_layer_onto(
            canvas,
            width,
            height,
            sub_pixels,
            width,
            height,
            x=0,
            y=0,
            opacity=node.opacity,
            composite_op=node.composite_op,
        )
    else:
        _render_children(
            node.children, canvas, width=width, height=height, resolve=resolve, limits=limits
        )


def render(
    root: OraStack,
    members: Mapping[str, bytes],
    *,
    width: int,
    height: int,
    limits: ResourceLimits = DEFAULT_LIMITS,
) -> DecodedRaster:
    """Composite `root`'s subtree deterministically into a single RGBA8
    image of `width` x `height` pixels.

    `root` is always treated as the top of a fresh isolated render, per the
    specification's own root-stack rule (module docstring). Passing an
    interior stack node here renders that subtree standalone the same way
    -- the format defines no other notion of "subtree rendering".

    `members` maps archive-root-relative member paths (as `OraLayer.src`
    values reference them) to their raw bytes, exactly the shape of
    `OraImage.members`.
    """
    _checked(
        (width, height, 4, 8),
        ceiling=limits.max_decompressed_bytes,
        label="ORA render canvas",
    )
    canvas = _new_transparent_canvas(width, height)
    _render_children(
        root.children,
        canvas,
        width=width,
        height=height,
        resolve=lambda src: _resolve_member(members, src),
        limits=limits,
    )
    pixels = _canvas_to_straight_rgba8(canvas, width, height)
    return DecodedRaster(width=width, height=height, pixels=pixels)


class Renderer(Protocol):
    """A pluggable rendering backend: given a stack/document subtree and
    its archive members, produce a composited RGBA8 image.

    ORA-COMPOSITE-001: "pixel semantics through a replaceable rendering
    adapter" -- this protocol IS that adapter boundary, previously absent
    (this module had "no adapter abstraction of any kind", per that
    obligation's own prior missing_behavior text). `render_document` and
    `generate_baseline_assets` both accept a `renderer:` parameter typed
    against this protocol, defaulting to `DEFAULT_RENDERER`
    (`W3CCompositingRenderer`, this module's own dependency-free W3C
    Compositing-and-Blending-Level-1 implementation). A caller may
    substitute any other object satisfying this same protocol -- a
    GPU-accelerated backend, one delegating to an external library, or a
    test double -- without any other function in this module changing.
    """

    def render(
        self,
        root: OraStack,
        members: Mapping[str, bytes],
        *,
        width: int,
        height: int,
        limits: ResourceLimits = DEFAULT_LIMITS,
    ) -> DecodedRaster: ...


@dataclass(frozen=True, slots=True)
class W3CCompositingRenderer:
    """The default `Renderer`: this module's own `render()` function,
    wrapped as an adapter instance. Stateless -- one instance
    (`DEFAULT_RENDERER`) is shared by every caller that does not supply
    its own renderer."""

    def render(
        self,
        root: OraStack,
        members: Mapping[str, bytes],
        *,
        width: int,
        height: int,
        limits: ResourceLimits = DEFAULT_LIMITS,
    ) -> DecodedRaster:
        return render(root, members, width=width, height=height, limits=limits)


#: The rendering adapter every caller gets unless it supplies its own.
DEFAULT_RENDERER: Renderer = W3CCompositingRenderer()


def _straight_over(
    src: tuple[float, float, float],
    alpha_s: float,
    dst: tuple[float, float, float],
    alpha_d: float,
) -> tuple[tuple[float, float, float], float]:
    """Porter-Duff "source over", derived independently in STRAIGHT-alpha
    space -- the classic textbook formula (out_a = a_s + a_d*(1-a_s);
    out_c = (a_s*c_s + a_d*(1-a_s)*c_d) / out_a) -- rather than
    `_composite_layer_onto`'s own premultiplied-canvas formulation
    (`new_r = alpha_s*blended + (1-alpha_s)*rb`, backdrop already carried
    premultiplied). Both are correct, standard formulations of the same
    Porter-Duff operator; deliberately re-derived from the definition
    rather than copied, so `ORA-COMPOSITE-001`'s own "adapter differential
    test" exercises a genuinely different arithmetic path, not the same
    code renamed."""
    out_a = alpha_s + alpha_d * (1.0 - alpha_s)
    if out_a <= 0.0:
        return (0.0, 0.0, 0.0), 0.0
    out = tuple(
        (alpha_s * src[i] + alpha_d * (1.0 - alpha_s) * dst[i]) / out_a for i in range(3)
    )
    return (out[0], out[1], out[2]), out_a


def _render_node_straight_alpha_reference(
    node: OraChild,
    canvas: dict[tuple[int, int], tuple[tuple[float, float, float], float]],
    *,
    width: int,
    height: int,
    resolve: Callable[[str], bytes],
    limits: ResourceLimits,
) -> None:
    """Independent recursive tree walker -- does not call `_render_node`
    or share any code with it -- for `render_straight_alpha_reference`'s
    own bounded differential-test scope (Normal blend, Source Over
    compositing only; see that function's own docstring)."""
    if not node.is_visible:
        return
    if isinstance(node, OraText):
        return
    info = composite_op_info(node.composite_op) or composite_op_info(DEFAULT_COMPOSITE_OP)
    assert info is not None
    if info.blending_function != "Normal" or info.compositing_operator != _SOURCE_OVER:
        raise OraValidationError(
            f"render_straight_alpha_reference only supports Normal/Source-Over; "
            f"{node.composite_op!r} resolves to blend={info.blending_function!r}, "
            f"operator={info.compositing_operator!r}"
        )
    if isinstance(node, OraLayer):
        raster = decode_png(resolve(node.src), limits=limits)
        x0, y0 = max(0, node.x), max(0, node.y)
        x1 = min(width, node.x + raster.width)
        y1 = min(height, node.y + raster.height)
        for cy in range(y0, y1):
            ry = cy - node.y
            raster_row = ry * raster.width * 4
            for cx in range(x0, x1):
                rx = cx - node.x
                o = raster_row + rx * 4
                alpha_s = (raster.pixels[o + 3] / 255.0) * node.opacity
                src = (
                    raster.pixels[o] / 255.0,
                    raster.pixels[o + 1] / 255.0,
                    raster.pixels[o + 2] / 255.0,
                )
                dst_colour, dst_alpha = canvas.get((cx, cy), ((0.0, 0.0, 0.0), 0.0))
                canvas[(cx, cy)] = _straight_over(src, alpha_s, dst_colour, dst_alpha)
        return
    # OraStack
    if node.is_isolated_group:
        sub_canvas: dict[tuple[int, int], tuple[tuple[float, float, float], float]] = {}
        for child in reversed(node.children):
            _render_node_straight_alpha_reference(
                child, sub_canvas, width=width, height=height, resolve=resolve, limits=limits
            )
        for (cx, cy), (colour, alpha) in sub_canvas.items():
            group_alpha = alpha * node.opacity
            dst_colour, dst_alpha = canvas.get((cx, cy), ((0.0, 0.0, 0.0), 0.0))
            canvas[(cx, cy)] = _straight_over(colour, group_alpha, dst_colour, dst_alpha)
    else:
        for child in reversed(node.children):
            _render_node_straight_alpha_reference(
                child, canvas, width=width, height=height, resolve=resolve, limits=limits
            )


def render_straight_alpha_reference(
    root: OraStack,
    members: Mapping[str, bytes],
    *,
    width: int,
    height: int,
    limits: ResourceLimits = DEFAULT_LIMITS,
) -> DecodedRaster:
    """A second, genuinely independent `Renderer` implementation --
    `ORA-COMPOSITE-001`'s own "adapter differential test" requirement,
    previously unmet because only test-double renderers existed (a
    minimal class and a stateful class, neither doing real pixel
    arithmetic of its own).

    Deliberately, honestly BOUNDED: this function raises
    `OraValidationError` for any node whose composite-op does not resolve
    to Normal blend + Source Over (the default, and the only combination
    every real sample in this package's own corpus uses) -- it does not
    attempt the other 14 blend functions or 5 other Porter-Duff operators
    `render()` supports. Building a second, independent implementation of
    the FULL blend-mode/operator matrix is a substantially larger
    undertaking, not attempted here; this function proves the adapter
    abstraction and the core Normal/Source-Over compositing math (the
    path every real corpus sample and the large majority of real-world
    OpenRaster documents actually use) against a genuinely different
    arithmetic derivation, not a full differential proof of every
    documented pixel semantic.

    Uses a sparse `{(x, y): (straight_rgb, straight_alpha)}` dict canvas
    (only touched pixels are stored) and explicit straight-alpha
    Porter-Duff "over" math (`_straight_over`) throughout -- `render()`'s
    own dense premultiplied-float array is never called or imported by
    this function; the two share no compositing code, only the already
    separately-tested `decode_png`/`composite_op_info` primitives.
    """
    _checked(
        (width, height, 4, 8),
        ceiling=limits.max_decompressed_bytes,
        label="ORA render canvas (straight-alpha reference)",
    )
    canvas: dict[tuple[int, int], tuple[tuple[float, float, float], float]] = {}
    for child in reversed(root.children):
        _render_node_straight_alpha_reference(
            child,
            canvas,
            width=width,
            height=height,
            resolve=lambda src: _resolve_member(members, src),
            limits=limits,
        )
    out = bytearray(width * height * 4)
    for (cx, cy), (colour, alpha) in canvas.items():
        i = (cy * width + cx) * 4
        out[i] = _clamp255(colour[0])
        out[i + 1] = _clamp255(colour[1])
        out[i + 2] = _clamp255(colour[2])
        out[i + 3] = _clamp255(alpha)
    return DecodedRaster(width=width, height=height, pixels=bytes(out))


@dataclass(frozen=True, slots=True)
class StraightAlphaReferenceRenderer:
    """`render_straight_alpha_reference()`, wrapped as a `Renderer`
    adapter instance -- the second, genuinely independent implementation
    `ORA-COMPOSITE-001`'s own "adapter differential test" exercises."""

    def render(
        self,
        root: OraStack,
        members: Mapping[str, bytes],
        *,
        width: int,
        height: int,
        limits: ResourceLimits = DEFAULT_LIMITS,
    ) -> DecodedRaster:
        return render_straight_alpha_reference(root, members, width=width, height=height, limits=limits)


def render_document(
    document: OraDocument,
    members: Mapping[str, bytes],
    *,
    limits: ResourceLimits = DEFAULT_LIMITS,
    renderer: Renderer = DEFAULT_RENDERER,
) -> DecodedRaster:
    """Render `document`'s full root stack at its own declared canvas
    size (`document.width` x `document.height`), via `renderer`
    (ORA-COMPOSITE-001's replaceable rendering adapter; defaults to this
    module's own W3C compositor, `DEFAULT_RENDERER`)."""
    return renderer.render(
        document.root, members, width=document.width, height=document.height, limits=limits
    )


def generate_baseline_assets(
    document: OraDocument,
    members: Mapping[str, bytes],
    *,
    limits: ResourceLimits = DEFAULT_LIMITS,
    renderer: Renderer = DEFAULT_RENDERER,
) -> tuple[bytes, bytes]:
    """Render `document` and return `(thumbnail_bytes, merged_image_bytes)`,
    ready for `lifecycle.replace_baseline_asset`.

    This is the "generate" half of ORA-BASELINEASSET-001 ("read, validate,
    generate, and replace required thumbnail and flattened-view assets"),
    previously unbuilt because no renderer existed -- see that obligation's
    prior note in `lifecycle.replace_baseline_asset`'s own docstring.

    `renderer` is the same replaceable rendering adapter `render_document`
    accepts (ORA-COMPOSITE-001).
    """
    rendered = render_document(document, members, limits=limits, renderer=renderer)
    merged_image = encode_png(rendered)
    thumbnail = generate_thumbnail(rendered)
    return thumbnail, merged_image


__all__ = [
    "DEFAULT_RENDERER",
    "DecodedRaster",
    "Renderer",
    "StraightAlphaReferenceRenderer",
    "W3CCompositingRenderer",
    "decode_png",
    "encode_png",
    "generate_baseline_assets",
    "generate_thumbnail",
    "render",
    "render_document",
    "render_straight_alpha_reference",
]
