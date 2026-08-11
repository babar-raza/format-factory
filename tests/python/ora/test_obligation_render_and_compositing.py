"""ORA-RENDER-001 / ORA-COMPOSITE-001 / ORA-ISOLATION-001 / ORA-STREAM-001 /
ORA-BASELINEASSET-001 against the shipped namespace.

MUST (ORA-RENDER-001): "Render documents and subtrees deterministically
with clipping, order, offsets, visibility, opacity, compositing, isolation,
color-mode, and resource-limit semantics documented."

required_tests: "Golden images, subtree rendering, clipping, resource
exhaustion, and adapter-version differential tests."

Golden-image proof here has two independent legs, both hand-verified rather
than taken on faith from either side:

1. Pixel values a human can check by hand from the standard W3C alpha
   -compositing formula (e.g. `test_render_applies_layer_opacity_and_alpha_
   compositing`), computed independently of this module's own arithmetic.
2. `render_document` against the project's own real `samples/by-format/ora`
   corpus, compared to each fixture's own embedded `mergedimage.png`.

Leg 2 surfaced a real, independent defect while this test file was being
written: `valid/multi-layer.ora`'s own `mergedimage.png` did not reflect
its own `stack.xml` at all (it was a raw copy of the Foreground layer's
PNG, opacity and background compositing both simply absent). That was
diagnosed against leg 1's hand-verified arithmetic, not assumed -- see
`samples/by-format/ora/_provenance.yaml`'s `correction_note` for that
fixture -- and the fixture was corrected using this same renderer
(`generate_baseline_assets`) before being used as a comparison target
here. `with-groups.ora` and `minimal.ora` needed no correction because
both use opacity 1.0 throughout, where a raw copy happens to equal the
correct composite.

None of this is claimed as independent-producer interoperability proof:
every sample in this corpus is project-owned synthetic content (see
`_provenance.yaml`), not output from a second OpenRaster application. That
remains open scope, consistent with this obligation's own release gate
("agrees with at least two independent producers/consumers") not being
attempted here.

ORA-STREAM-001's own missing_behavior named one further gap this file now
closes: the render budget (canvas allocation, per-layer decompression) had
only ever been exercised one dimension at a time. The "Combined 'large
sparse archive' render-budget stress case" section below builds one
document combining many layers (40+), deep isolation nesting (20 levels),
and a canvas sized to within 0.1% of its own resource-limit budget, and
proves the budget holds correctly under that combined load -- both that a
within-budget combined scenario still renders the correct result, and that
an over-budget combined scenario is still correctly refused, not silently
bypassed because other dimensions were also near their own limits.
"""

from __future__ import annotations

import struct
import zlib

import pytest

import dataclasses

from format_factory.core import ResourceLimits
from format_factory.ora import (
    OraDocument,
    OraImage,
    OraLayer,
    OraLimitError,
    OraStack,
    OraText,
    OraValidationError,
    apply_transaction,
    decode_png,
    dumps,
    encode_png,
    generate_baseline_assets,
    generate_thumbnail,
    load,
    render,
    render_document,
    replace_baseline_asset,
    validate,
)
from format_factory.ora.render import DecodedRaster

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


# ── Local PNG builders (bit-exact, independent of format_factory.ora.render's
# own encoder) ────────────────────────────────────────────────────────────


def _chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def solid_rgba_png(width: int, height: int, rgba: tuple[int, int, int, int]) -> bytes:
    """An 8-bit truecolour+alpha PNG, every pixel `rgba`, filter type None."""
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    row = bytes([0]) + bytes(rgba) * width
    raw = row * height
    return (
        PNG_SIGNATURE
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(raw))
        + _chunk(b"IEND", b"")
    )


def raw_png(width: int, height: int, *, bit_depth: int, colour_type: int, interlace: int = 0) -> bytes:
    """Header-only-correct PNG (undersized IDAT) -- for tests that only
    reach IHDR-level rejection (e.g. interlace) and never decode pixels."""
    ihdr = struct.pack(">IIBBBBB", width, height, bit_depth, colour_type, 0, 0, interlace)
    return (
        PNG_SIGNATURE
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(b"\0" * 4))
        + _chunk(b"IEND", b"")
    )


def indexed_png(width: int, height: int, indices: list[int], palette: bytes) -> bytes:
    """An 8-bit indexed-colour PNG with the given per-pixel palette indices."""
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 3, 0, 0, 0)
    rows = []
    for y in range(height):
        row = indices[y * width : (y + 1) * width]
        rows.append(bytes([0]) + bytes(row))
    raw = b"".join(rows)
    return (
        PNG_SIGNATURE
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"PLTE", palette)
        + _chunk(b"IDAT", zlib.compress(raw))
        + _chunk(b"IEND", b"")
    )


# ── PNG codec round trip ────────────────────────────────────────────────


def test_decode_png_round_trips_through_encode_png() -> None:
    pixels = bytes(
        v
        for y in range(3)
        for x in range(2)
        for v in (x * 40, y * 60, 10, 255 - (x + y) * 20)
    )
    raster = DecodedRaster(width=2, height=3, pixels=pixels)

    decoded = decode_png(encode_png(raster))

    assert decoded.width == 2
    assert decoded.height == 3
    assert decoded.pixels == pixels


def test_decode_png_reads_indexed_colour_via_palette() -> None:
    palette = bytes((10, 20, 30)) + bytes((200, 100, 50))
    payload = indexed_png(2, 1, [0, 1], palette)

    decoded = decode_png(payload)

    assert decoded.pixels == bytes((10, 20, 30, 255, 200, 100, 50, 255))


def test_interlaced_png_is_refused_not_misdecoded() -> None:
    payload = raw_png(4, 4, bit_depth=8, colour_type=6, interlace=1)

    with pytest.raises(OraValidationError, match="interlac"):
        decode_png(payload)


def test_corrupt_chunk_crc_is_rejected() -> None:
    payload = bytearray(solid_rgba_png(2, 2, (1, 2, 3, 255)))
    payload[-5] ^= 0xFF  # flip a byte inside the IEND chunk's CRC

    with pytest.raises(OraValidationError, match="CRC"):
        decode_png(bytes(payload))


# ── Single-layer placement, visibility, offsets, clipping ──────────────


def test_render_single_opaque_layer_equals_its_own_pixels() -> None:
    layer_bytes = solid_rgba_png(4, 4, (10, 20, 30, 255))
    root = OraStack(children=(OraLayer(src="l.png"),))

    result = render(root, {"l.png": layer_bytes}, width=4, height=4)

    assert result.pixels == decode_png(layer_bytes).pixels


def test_hidden_layer_contributes_nothing() -> None:
    layer_bytes = solid_rgba_png(2, 2, (255, 0, 0, 255))
    root = OraStack(children=(OraLayer(src="l.png", visibility="hidden"),))

    result = render(root, {"l.png": layer_bytes}, width=2, height=2)

    assert result.pixels == bytes(2 * 2 * 4)  # fully transparent canvas


def test_text_element_is_skipped_not_rendered() -> None:
    root = OraStack(children=(OraText(name="caption"),))

    result = render(root, {}, width=2, height=2)

    assert result.pixels == bytes(2 * 2 * 4)


def test_layer_offset_places_pixels_at_the_declared_position() -> None:
    layer_bytes = solid_rgba_png(1, 1, (9, 8, 7, 255))
    root = OraStack(children=(OraLayer(src="l.png", x=2, y=1),))

    result = render(root, {"l.png": layer_bytes}, width=4, height=4)

    def pixel(x: int, y: int) -> bytes:
        o = (y * 4 + x) * 4
        return result.pixels[o : o + 4]

    assert pixel(2, 1) == bytes((9, 8, 7, 255))
    assert pixel(0, 0) == bytes(4)
    assert pixel(3, 1) == bytes(4)


def test_layer_partially_off_canvas_is_clipped_not_wrapped_or_rejected() -> None:
    layer_bytes = solid_rgba_png(4, 4, (1, 1, 1, 255))
    root = OraStack(children=(OraLayer(src="l.png", x=-2, y=-2),))

    result = render(root, {"l.png": layer_bytes}, width=4, height=4)

    def pixel(x: int, y: int) -> bytes:
        o = (y * 4 + x) * 4
        return result.pixels[o : o + 4]

    # Only the 2x2 overlap (canvas [0,2)x[0,2), layer local [2,4)x[2,4)) paints.
    assert pixel(0, 0) == bytes((1, 1, 1, 255))
    assert pixel(1, 1) == bytes((1, 1, 1, 255))
    assert pixel(2, 2) == bytes(4)
    assert pixel(3, 3) == bytes(4)


def test_layer_entirely_off_canvas_paints_nothing() -> None:
    layer_bytes = solid_rgba_png(2, 2, (1, 1, 1, 255))
    root = OraStack(children=(OraLayer(src="l.png", x=100, y=100),))

    result = render(root, {"l.png": layer_bytes}, width=4, height=4)

    assert result.pixels == bytes(4 * 4 * 4)


def test_layer_paints_over_layer_below_it_in_document_order() -> None:
    # "its first child is the uppermost item" -- top listed first must win.
    top = solid_rgba_png(2, 2, (255, 0, 0, 255))
    bottom = solid_rgba_png(2, 2, (0, 255, 0, 255))
    root = OraStack(children=(OraLayer(src="top.png"), OraLayer(src="bottom.png")))

    result = render(root, {"top.png": top, "bottom.png": bottom}, width=2, height=2)

    assert result.pixels[0:4] == bytes((255, 0, 0, 255))


def test_missing_layer_source_raises() -> None:
    root = OraStack(children=(OraLayer(src="absent.png"),))

    with pytest.raises(OraValidationError, match="absent.png"):
        render(root, {}, width=2, height=2)


# ── Alpha compositing and blend functions, hand-verified ───────────────


def test_render_applies_layer_opacity_and_alpha_compositing() -> None:
    """The exact scenario `samples/by-format/ora/valid/multi-layer.ora`
    exercises: an 80%-opacity, already-semi-transparent blue layer over an
    opaque white background.

    Hand computation (straight alpha, source-over):
      alpha_s = (200/255) * 0.8 = 0.6274509803921569
      new_r = new_g = (1 - alpha_s) * 255 = 95.0000... -> round 95
      new_b = alpha_s*255 + (1-alpha_s)*255 = 255
      new_a = alpha_s + 1.0*(1-alpha_s) = 1.0 -> 255
    """
    fg = solid_rgba_png(1, 1, (0, 0, 255, 200))
    bg = solid_rgba_png(1, 1, (255, 255, 255, 255))
    root = OraStack(
        children=(
            OraLayer(src="fg.png", opacity=0.8),
            OraLayer(src="bg.png"),
        )
    )

    result = render(root, {"fg.png": fg, "bg.png": bg}, width=1, height=1)

    assert result.pixels == bytes((95, 95, 255, 255))


def test_render_matches_corrected_multi_layer_fixture() -> None:
    image = load("samples/by-format/ora/valid/multi-layer.ora")

    rendered = render_document(image.document, image.members)
    embedded = decode_png(image.members["mergedimage.png"])

    assert rendered.pixels == embedded.pixels
    assert rendered.pixels == bytes((95, 95, 255, 255)) * (
        image.document.width * image.document.height
    )


@pytest.mark.parametrize(
    "fixture",
    [
        "samples/by-format/ora/valid/minimal.ora",
        "samples/by-format/ora/valid/with-groups.ora",
    ],
)
def test_render_matches_embedded_merged_image_for_opaque_fixtures(fixture: str) -> None:
    image = load(fixture)

    rendered = render_document(image.document, image.members)
    embedded = decode_png(image.members["mergedimage.png"])

    assert rendered.pixels == embedded.pixels


def test_multiply_blend_matches_hand_computed_value() -> None:
    """svg:multiply, both layers fully opaque: Co = Cb*Cs per channel,
    computed here independently of render.py's own blend table."""
    top_rgb = (200, 50, 10)
    bottom_rgb = (100, 250, 90)
    top = solid_rgba_png(1, 1, (*top_rgb, 255))
    bottom = solid_rgba_png(1, 1, (*bottom_rgb, 255))
    root = OraStack(
        children=(
            OraLayer(src="top.png", composite_op="svg:multiply"),
            OraLayer(src="bottom.png"),
        )
    )

    result = render(root, {"top.png": top, "bottom.png": bottom}, width=1, height=1)

    expected = tuple(
        round((cb / 255.0) * (cs / 255.0) * 255.0) for cb, cs in zip(bottom_rgb, top_rgb)
    )
    assert result.pixels[:3] == bytes(expected)
    assert result.pixels[3] == 255


def test_screen_blend_matches_hand_computed_value() -> None:
    """svg:screen: Co = Cb + Cs - Cb*Cs, both layers fully opaque."""
    top_rgb = (60, 200, 0)
    bottom_rgb = (120, 30, 255)
    top = solid_rgba_png(1, 1, (*top_rgb, 255))
    bottom = solid_rgba_png(1, 1, (*bottom_rgb, 255))
    root = OraStack(
        children=(
            OraLayer(src="top.png", composite_op="svg:screen"),
            OraLayer(src="bottom.png"),
        )
    )

    result = render(root, {"top.png": top, "bottom.png": bottom}, width=1, height=1)

    def screen(cb: int, cs: int) -> int:
        b, s = cb / 255.0, cs / 255.0
        return round((b + s - b * s) * 255.0)

    expected = tuple(screen(cb, cs) for cb, cs in zip(bottom_rgb, top_rgb))
    assert result.pixels[:3] == bytes(expected)


def test_unrecognized_composite_op_falls_back_to_default_rather_than_raising() -> None:
    """composite-op is a deliberately open vocabulary (model/composite_ops.py);
    rendering a forward-compatible value it does not recognise falls back to
    svg:src-over rather than inventing or rejecting."""
    layer = solid_rgba_png(1, 1, (5, 6, 7, 255))
    root = OraStack(children=(OraLayer(src="l.png", composite_op="vendor:unknown-mode"),))

    result = render(root, {"l.png": layer}, width=1, height=1)

    assert result.pixels == bytes((5, 6, 7, 255))


# ── Non-default Porter-Duff operators ───────────────────────────────────
#
# Found via ORA-COMPOSITE-001's own full-inventory producer-verification
# sweep (2026-08-12): a real, independent mathematical oracle
# (tools/ora/producer_harness/composite_oracle.py, re-derived from Porter &
# Duff (1984) independently of this module's own arithmetic) disagreed with
# format-factory's own render() for exactly 2 of the 6 registered Porter-Duff
# operators, at points OUTSIDE the source layer's own declared raster
# bounds. Root cause: _composite_layer_onto only ever iterates the
# intersection of the canvas and the source layer's own raster bounds --
# correct for Source Over/Lighter/Destination Out/Source Atop, whose own
# Fb coefficient equals 1.0 (i.e. "leave the destination unchanged") at
# alpha_s=0, so skipping out-of-bounds pixels coincidentally produces the
# right answer for those 4. It is NOT correct for Destination In and
# Destination Atop, whose own Fb equals alpha_s -- 0.0 outside the source
# layer's bounds, meaning the destination must be CLEARED there, not left
# untouched. Confirmed by direct computation
# (porter_duff_coeffs('Destination In', alpha_s=0.0, alpha_b=0.6) ==
# (0.0, 0.0), not (0.0, 1.0)) before this test was written, not guessed.


def test_destination_in_clears_the_destination_outside_the_source_layers_own_bounds() -> None:
    """Porter & Duff (1984): Destination In has Fa=0, Fb=alpha_s. Where the
    source layer has no pixel data at all (alpha_s=0 by definition, not
    merely by transparency), Fb=0 too -- the destination must be cleared to
    fully transparent, not left as whatever it was before this operator was
    applied. A 1x1 canvas with a destination layer covering it and a source
    layer covering NONE of it (built via an empty raster placed outside the
    canvas) isolates exactly this case."""
    destination = solid_rgba_png(2, 2, (230, 60, 40, 153))
    # 1x1 source placed at (5,5) -- entirely outside the 2x2 canvas, so
    # every canvas pixel is "outside the source layer's own bounds".
    source = solid_rgba_png(1, 1, (40, 120, 230, 128))
    root = OraStack(
        children=(
            OraLayer(src="source.png", composite_op="svg:dst-in", x=5, y=5),
            OraLayer(src="destination.png"),
        )
    )

    result = render(root, {"source.png": source, "destination.png": destination}, width=2, height=2)

    assert result.pixels == bytes(16)  # fully transparent everywhere -- no source coverage anywhere


def test_destination_atop_clears_the_destination_outside_the_source_layers_own_bounds() -> None:
    """Porter & Duff (1984): Destination Atop has Fb=alpha_s (same as
    Destination In for this specific edge case) -- 0 where the source layer
    does not cover the canvas at all, clearing the destination there too."""
    destination = solid_rgba_png(2, 2, (230, 60, 40, 153))
    source = solid_rgba_png(1, 1, (40, 120, 230, 128))
    root = OraStack(
        children=(
            OraLayer(src="source.png", composite_op="svg:dst-atop", x=5, y=5),
            OraLayer(src="destination.png"),
        )
    )

    result = render(root, {"source.png": source, "destination.png": destination}, width=2, height=2)

    assert result.pixels == bytes(16)


def test_destination_out_and_source_atop_correctly_leave_destination_unchanged_outside_source_bounds() -> None:
    """Sibling operators to the 2 above, whose own Fb coefficient genuinely
    does equal 1.0 (unchanged) at alpha_s=0 -- included as a contrast case
    so the 2 fixed operators above are not mistaken for a blanket
    'always clear outside source bounds' rule, which would be equally
    wrong (it would break these 2)."""
    destination = solid_rgba_png(2, 2, (230, 60, 40, 153))
    source = solid_rgba_png(1, 1, (40, 120, 230, 128))
    expected = bytes((230, 60, 40, 153)) * 4

    for composite_op in ("svg:dst-out", "svg:src-atop"):
        root = OraStack(
            children=(
                OraLayer(src="source.png", composite_op=composite_op, x=5, y=5),
                OraLayer(src="destination.png"),
            )
        )
        result = render(root, {"source.png": source, "destination.png": destination}, width=2, height=2)
        assert result.pixels == expected, f"{composite_op} unexpectedly changed outside source bounds"


# ── Isolation ────────────────────────────────────────────────────────────


def test_isolated_group_applies_group_opacity_once_not_per_child() -> None:
    """Two fully-opaque, overlapping children inside an isolated group at
    group opacity 0.5, over an opaque black backdrop.

    If opacity were (wrongly) applied per child instead of once to the
    flattened group, the top child would still fully occlude the bottom
    child before the backdrop ever showed through, and the group's own
    0.5 would only fade the top child -- giving grey (127,127,127), not
    the isolated-group answer.

    Correct (isolated) result: render both children fully opaque first
    (top red fully occludes bottom green -> pure red), THEN blend that
    flattened group at 0.5 over black: 0.5*255 + 0.5*0 = 127.5 -> 128 (R),
    0 (G, B unchanged at 0 either way).
    """
    top = solid_rgba_png(1, 1, (255, 0, 0, 255))
    bottom = solid_rgba_png(1, 1, (0, 255, 0, 255))
    backdrop = solid_rgba_png(1, 1, (0, 0, 0, 255))
    group = OraStack(
        isolation="isolate",
        opacity=0.5,
        children=(OraLayer(src="top.png"), OraLayer(src="bottom.png")),
    )
    root = OraStack(children=(group, OraLayer(src="backdrop.png")))

    result = render(
        root,
        {"top.png": top, "bottom.png": bottom, "backdrop.png": backdrop},
        width=1,
        height=1,
    )

    assert result.pixels == bytes((128, 0, 0, 255))


def test_non_isolated_auto_group_is_equivalent_to_no_group_at_all() -> None:
    top = solid_rgba_png(1, 1, (10, 20, 30, 200))
    bottom = solid_rgba_png(1, 1, (200, 190, 180, 255))
    members = {"top.png": top, "bottom.png": bottom}

    grouped = OraStack(
        children=(
            OraStack(
                isolation="auto",
                children=(OraLayer(src="top.png"), OraLayer(src="bottom.png")),
            ),
        )
    )
    flat = OraStack(children=(OraLayer(src="top.png"), OraLayer(src="bottom.png")))

    grouped_result = render(grouped, members, width=1, height=1)
    flat_result = render(flat, members, width=1, height=1)

    assert grouped_result.pixels == flat_result.pixels


def test_stack_x_and_y_are_ignored_for_both_isolated_and_non_isolated_groups() -> None:
    """"For a non-root stack, x and y are ignored. ... The offset of the
    contained layers is solely defined by their own x and y attributes"
    (File Layout Specification). A stack declaring a nonzero x/y must not
    shift its children."""
    layer = solid_rgba_png(1, 1, (7, 7, 7, 255))
    isolated_group = OraStack(isolation="isolate", x=5, y=5, children=(OraLayer(src="l.png"),))
    auto_group = OraStack(x=5, y=5, children=(OraLayer(src="l.png"),))

    isolated_result = render(OraStack(children=(isolated_group,)), {"l.png": layer}, width=1, height=1)
    auto_result = render(OraStack(children=(auto_group,)), {"l.png": layer}, width=1, height=1)

    assert isolated_result.pixels == bytes((7, 7, 7, 255))
    assert auto_result.pixels == bytes((7, 7, 7, 255))


# ── Subtree rendering ────────────────────────────────────────────────────


def test_render_accepts_an_interior_subtree_not_only_the_document_root() -> None:
    image = load("samples/by-format/ora/valid/with-groups.ora")
    group_a = image.document.root.children[0]
    assert group_a.name == "Group A"

    # Rendered standalone, the subtree is its own implicit isolated render
    # (module docstring) -- independent of it also being isolated when
    # composited into the full document.
    subtree_result = render(
        group_a, image.members, width=image.document.width, height=image.document.height
    )

    assert subtree_result.width == image.document.width
    assert subtree_result.height == image.document.height
    # Group A's own two children (A1 opaque over A2) fully cover the canvas,
    # so the subtree alone must already be fully opaque.
    assert all(subtree_result.pixels[i] == 255 for i in range(3, len(subtree_result.pixels), 4))


# ── Adapter-version differential ────────────────────────────────────────


def test_rendering_ignores_declared_profile_version_and_uses_real_semantics() -> None:
    """A document that declares an old profile (0.0.1, before isolation
    existed) but uses isolation-triggering attributes must still render
    with real isolation semantics -- the renderer follows the document's
    actual content, the same way `_version_drift_diagnostics` already
    treats this as a warning rather than a silent behavior change."""
    top = solid_rgba_png(1, 1, (255, 0, 0, 255))
    bottom = solid_rgba_png(1, 1, (0, 255, 0, 255))
    backdrop = solid_rgba_png(1, 1, (0, 0, 0, 255))
    group = OraStack(opacity=0.5, children=(OraLayer(src="top.png"), OraLayer(src="bottom.png")))
    old_root = OraStack(children=(group, OraLayer(src="backdrop.png")))
    old_document = OraDocument(width=1, height=1, version="0.0.1", root=old_root)

    result = render_document(
        old_document, {"top.png": top, "bottom.png": bottom, "backdrop.png": backdrop}
    )

    assert result.pixels == bytes((128, 0, 0, 255))


# ── Resource limits ──────────────────────────────────────────────────────


def test_oversized_canvas_raises_resource_limit_error_before_allocating() -> None:
    tiny_limits = ResourceLimits(max_decompressed_bytes=1024)
    root = OraStack(children=())

    with pytest.raises(OraLimitError):
        render(root, {}, width=10_000, height=10_000, limits=tiny_limits)


def test_oversized_layer_raster_is_rejected_before_decompression() -> None:
    tiny_limits = ResourceLimits(max_decompressed_bytes=64)
    payload = raw_png(10_000, 10_000, bit_depth=8, colour_type=6)

    with pytest.raises(OraLimitError):
        decode_png(payload, limits=tiny_limits)


def test_truncated_idat_stream_is_rejected_not_zero_padded() -> None:
    ihdr = struct.pack(">IIBBBBB", 4, 4, 8, 6, 0, 0, 0)
    short_raw = zlib.compress(b"\0" * 8)  # far short of the 4*(1+16)=68 bytes needed
    payload = (
        PNG_SIGNATURE + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", short_raw) + _chunk(b"IEND", b"")
    )

    with pytest.raises(OraValidationError, match="decompressed"):
        decode_png(payload)


# ── Combined "large sparse archive" render-budget stress case ───────────
#
# ORA-STREAM-001's own missing_behavior: the two tests above each isolate
# a single resource-limit dimension (canvas size, one layer's declared
# size). These two prove the render budget holds under a combined worst
# case -- many layers, deep isolation nesting, and a near-limit canvas,
# all at once -- rather than three dimensions that have only ever been
# exercised apart from each other.


def _small_opaque_layer(index: int) -> tuple[str, bytes]:
    name = f"deep-{index}.png"
    colour = (index % 256, (index * 7) % 256, (index * 13) % 256, 255)
    return name, solid_rgba_png(4, 4, colour)


def _deep_sparse_subtree(
    depth: int, layers_per_level: int, members: dict[str, bytes], counter: list[int]
) -> OraStack:
    """A stack `depth` levels deep, each level isolated and holding
    `layers_per_level` small opaque layers plus (except at the bottom) one
    nested child stack -- entirely covered by a real opaque layer stacked
    above it elsewhere in the document, so it contributes nothing to the
    final composited result but is still fully walked, decoded, and
    isolated-group-composited by the renderer, exactly like a real archive
    with far more structure than visible content."""
    leaves = []
    for _ in range(layers_per_level):
        name, payload = _small_opaque_layer(counter[0])
        counter[0] += 1
        members[name] = payload
        leaves.append(OraLayer(src=name))
    if depth <= 0:
        return OraStack(isolation="isolate", children=tuple(leaves))
    nested = _deep_sparse_subtree(depth - 1, layers_per_level, members, counter)
    return OraStack(isolation="isolate", children=(nested, *leaves))


def test_a_large_sparse_archive_with_deep_nesting_and_near_limit_canvas_renders_correctly_within_budget() -> None:
    tiny_limits = ResourceLimits(max_decompressed_bytes=200_000)
    # render()'s own canvas check is width * height * channels(4) *
    # bit_depth(8) against max_decompressed_bytes (confirmed directly
    # against render.py's own `_checked((width, height, 4, 8), ...)`
    # call, not assumed from its prose description) -- 71*88*4*8 =
    # 199,936 bytes, 99.97% of this budget.
    width, height = 71, 88
    top_layer_bytes = solid_rgba_png(width, height, (5, 100, 200, 255))
    members: dict[str, bytes] = {"top.png": top_layer_bytes}
    counter = [0]
    sparse_subtree = _deep_sparse_subtree(depth=20, layers_per_level=2, members=members, counter=counter)
    root = OraStack(children=(OraLayer(src="top.png"), sparse_subtree))
    assert len(members) >= 40  # genuinely "many layers", not a token few

    result = render(root, members, width=width, height=height, limits=tiny_limits)

    # The topmost layer is opaque and covers the full canvas -- per visual
    # stacking order (first child = uppermost), the entire deeply nested,
    # many-layered subtree beneath it is fully covered and must not change
    # the result, regardless of how much of it the renderer had to walk
    # and decode, within budget, to get there.
    assert result.pixels == decode_png(top_layer_bytes).pixels


def test_the_same_combined_scenario_over_the_canvas_budget_is_still_correctly_refused() -> None:
    """Proves the canvas budget check still fires correctly when layer
    count and nesting depth are simultaneously near their own limits --
    not only in isolation, where nothing else competes for the same
    resource-limit machinery's attention."""
    tiny_limits = ResourceLimits(max_decompressed_bytes=200_000)
    width, height = 71, 89  # 71*89*4*8 = 202,208 bytes -- just over the same budget
    members: dict[str, bytes] = {"top.png": solid_rgba_png(4, 4, (5, 100, 200, 255))}
    counter = [0]
    sparse_subtree = _deep_sparse_subtree(depth=20, layers_per_level=2, members=members, counter=counter)
    root = OraStack(children=(OraLayer(src="top.png"), sparse_subtree))
    assert len(members) >= 40

    with pytest.raises(OraLimitError):
        render(root, members, width=width, height=height, limits=tiny_limits)


# ── Baseline asset generation (ORA-BASELINEASSET-001's "generate" half) ──


def test_generate_baseline_assets_are_accepted_by_replace_baseline_asset() -> None:
    image = load("samples/by-format/ora/valid/with-groups.ora")

    thumbnail, merged_image = generate_baseline_assets(image.document, image.members)
    updated = replace_baseline_asset(image, thumbnail=thumbnail, merged_image=merged_image)

    report = validate(dumps(updated))
    assert not any(
        "BASELINE" in d.code or "MERGED_IMAGE" in d.code or "THUMBNAIL" in d.code
        for d in report.diagnostics
    )


def test_regenerated_baseline_assets_reflect_a_committed_transaction_edit() -> None:
    """ORA-EDIT-001's own required_tests names "stale-view invalidation";
    transaction.py's module docstring previously disclosed no rendering
    engine existed to make a stale view fresh again. Now one does: after a
    committed edit hides the top group, regenerating the baseline assets
    from the EDITED document must show the Base layer underneath, not the
    pre-edit view.
    """
    image = load("samples/by-format/ora/valid/with-groups.ora")
    group_a, base = image.document.root.children
    original_merged = decode_png(image.members["mergedimage.png"])
    base_raster = decode_png(image.members[base.src])

    def hide_group_a(img: OraImage) -> OraImage:
        hidden = dataclasses.replace(group_a, visibility="hidden")
        new_root = dataclasses.replace(img.document.root, children=(hidden, base))
        new_document = dataclasses.replace(img.document, root=new_root)
        return dataclasses.replace(img, document=new_document)

    result = apply_transaction(image, [hide_group_a])
    assert result.committed is True

    _, regenerated_merged_bytes = generate_baseline_assets(
        result.image.document, result.image.members
    )
    regenerated = decode_png(regenerated_merged_bytes)

    assert regenerated.pixels != original_merged.pixels
    assert regenerated.pixels == base_raster.pixels


def test_generate_thumbnail_downscales_oversized_renders_to_fit_the_bound() -> None:
    raster = DecodedRaster(width=600, height=300, pixels=bytes(600 * 300 * 4))

    thumbnail_bytes = generate_thumbnail(raster)
    decoded = decode_png(thumbnail_bytes)

    assert decoded.width <= 256
    assert decoded.height <= 256
    assert decoded.width == 256  # the wider dimension hits the bound exactly
    assert decoded.height == 128  # 300 * (256/600), rounded
