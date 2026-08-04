"""Read raster metadata from a PNG header without decoding it (ORA-ASSET-001).

"expose raster metadata before decode" is the requirement, and it is the whole
point of this module. A layer's raster may be enormous or a decompression bomb,
so a caller has to learn its dimensions and depth *before* committing to
decoding. Everything here is answered from the IHDR chunk — the 25 bytes
immediately after the 8-byte signature — and no pixel data is ever inflated.

That also means a file whose compressed pixel data is corrupt still yields
correct metadata, which is the behaviour a bounded reader wants: report the
declared shape, let the caller decide whether to spend the decode.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

from format_factory.core import DEFAULT_LIMITS, CheckedArithmeticError, ResourceLimits, checked_product

from ..errors import OraLimitError, OraValidationError

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
IHDR_LENGTH = 13
#: signature + 4-byte length + 4-byte type + 13-byte IHDR payload.
_HEADER_BYTES = len(PNG_SIGNATURE) + 8 + IHDR_LENGTH

#: PNG permits only these bit depths, and only some pair with each colour type.
VALID_BIT_DEPTHS = frozenset({1, 2, 4, 8, 16})

#: colour type -> (samples per pixel, permitted bit depths)
COLOUR_TYPES: dict[int, tuple[int, frozenset[int]]] = {
    0: (1, frozenset({1, 2, 4, 8, 16})),   # greyscale
    2: (3, frozenset({8, 16})),            # truecolour
    3: (1, frozenset({1, 2, 4, 8})),       # indexed
    4: (2, frozenset({8, 16})),            # greyscale + alpha
    6: (4, frozenset({8, 16})),            # truecolour + alpha
}

THUMBNAIL_MAX_EDGE = 256
THUMBNAIL_BIT_DEPTH = 8
MERGED_IMAGE_BIT_DEPTHS = frozenset({8, 16})


@dataclass(frozen=True)
class RasterMetadata:
    """What a PNG declares about itself, read without decoding it."""

    width: int
    height: int
    bit_depth: int
    colour_type: int
    interlaced: bool

    @property
    def channels(self) -> int:
        return COLOUR_TYPES[self.colour_type][0]

    @property
    def declared_byte_size(self) -> int:
        """Bytes an unpacked surface would occupy.

        Depth and channel count both matter: 16-bit RGBA is eight bytes per
        pixel, so a budget check that counted pixels alone would under-estimate
        by a factor of eight.
        """
        return self.width * self.height * self.channels * (self.bit_depth // 8 or 1)

    def satisfies_thumbnail_constraints(self) -> bool:
        """"must be a non-interlaced PNG with 8 bits per channel, and must not
        exceed 256 by 256 pixels.\""""
        return (
            not self.interlaced
            and self.bit_depth == THUMBNAIL_BIT_DEPTH
            and self.width <= THUMBNAIL_MAX_EDGE
            and self.height <= THUMBNAIL_MAX_EDGE
        )

    def satisfies_merged_image_constraints(self) -> bool:
        """"the final rendered image as a PNG with 8 or 16 bits per channel.\""""
        return self.bit_depth in MERGED_IMAGE_BIT_DEPTHS


def read_png_metadata(
    payload: bytes, *, limits: ResourceLimits = DEFAULT_LIMITS
) -> RasterMetadata:
    """Parse a PNG's IHDR. Never inflates pixel data."""
    if not payload.startswith(PNG_SIGNATURE):
        raise OraValidationError(
            "asset is not a PNG: the file does not begin with the PNG signature"
        )

    if len(payload) < _HEADER_BYTES:
        raise OraValidationError(
            f"asset is truncated: {len(payload)} bytes is too short to hold a "
            f"PNG header, which needs {_HEADER_BYTES}"
        )

    length, kind = struct.unpack(">I4s", payload[8:16])
    if kind != b"IHDR":
        # Reading dimensions from wherever IHDR happens to appear would let a
        # crafted file disagree with every other decoder about its own size.
        raise OraValidationError(
            f"asset is not a valid PNG: the first chunk must be IHDR, got "
            f"{kind.decode('ascii', 'replace')!r}"
        )
    if length != IHDR_LENGTH:
        raise OraValidationError(
            f"asset has a malformed IHDR chunk of {length} bytes, expected {IHDR_LENGTH}"
        )

    width, height, bit_depth, colour_type, compression, filter_method, interlace = (
        struct.unpack(">IIBBBBB", payload[16:_HEADER_BYTES])
    )

    if width == 0 or height == 0:
        raise OraValidationError(
            f"asset declares a zero dimension ({width}x{height}); PNG requires both "
            "to be positive"
        )

    if bit_depth not in VALID_BIT_DEPTHS:
        raise OraValidationError(
            f"asset declares bit depth {bit_depth}; PNG permits only "
            f"{sorted(VALID_BIT_DEPTHS)}"
        )

    if colour_type not in COLOUR_TYPES:
        raise OraValidationError(
            f"asset declares colour type {colour_type}; PNG permits only "
            f"{sorted(COLOUR_TYPES)}"
        )

    permitted = COLOUR_TYPES[colour_type][1]
    if bit_depth not in permitted:
        raise OraValidationError(
            f"asset declares bit depth {bit_depth} with colour type {colour_type}, "
            f"which permits only {sorted(permitted)}"
        )

    if compression != 0:
        raise OraValidationError(
            f"asset declares compression method {compression}; PNG defines only 0"
        )
    if filter_method != 0:
        raise OraValidationError(
            f"asset declares filter method {filter_method}; PNG defines only 0"
        )
    if interlace not in (0, 1):
        raise OraValidationError(
            f"asset declares interlace method {interlace}; PNG defines only 0 and 1"
        )

    channels, _ = COLOUR_TYPES[colour_type]
    bytes_per_sample = bit_depth // 8 or 1
    # A 16-byte file can declare a 40-gigapixel image. That declaration is what
    # a caller allocates against, so it is bounded before it is believed.
    try:
        checked_product(
            (width, height, channels, bytes_per_sample),
            ceiling=limits.max_decompressed_bytes,
            label="declared raster byte size",
        )
    except CheckedArithmeticError as exc:
        raise OraLimitError(
            f"asset declares {width}x{height} at {bit_depth}-bit with {channels} "
            f"channels, over the caller's byte budget: {exc}"
        ) from exc

    return RasterMetadata(
        width=width,
        height=height,
        bit_depth=bit_depth,
        colour_type=colour_type,
        interlaced=interlace == 1,
    )


__all__ = [
    "COLOUR_TYPES",
    "MERGED_IMAGE_BIT_DEPTHS",
    "PNG_SIGNATURE",
    "THUMBNAIL_BIT_DEPTH",
    "THUMBNAIL_MAX_EDGE",
    "VALID_BIT_DEPTHS",
    "RasterMetadata",
    "read_png_metadata",
]
