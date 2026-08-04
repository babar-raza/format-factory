"""ORA-ASSET-001 — referenced raster assets.

"Resolve archive-root-relative asset references safely; expose raster metadata
before decode; validate existence, media type, dimensions, channel depth, and
declared resource budgets."

"before decode" is the load-bearing phrase. A layer's raster may be enormous, or
a decompression bomb, and a caller has to be able to ask how big it is *before*
committing to decoding it. So metadata comes from the PNG IHDR chunk — the first
25 bytes after the signature — and never from decoding pixels.

Other rules quoted where they bind:

  "Layer data files are conventionally stored below data/ and are referenced
   from stack.xml using complete paths relative to the archive root."
  "Thumbnails/thumbnail.png is required, must be a non-interlaced PNG with 8
   bits per channel, and must not exceed 256 by 256 pixels."
  "mergedimage.png is mandatory since profile 0.0.2 and contains the final
   rendered image as a PNG with 8 or 16 bits per channel."
"""

from __future__ import annotations

import struct
import zlib

import pytest

from format_factory.core import ResourceLimits
from format_factory.ora import (
    OraArchiveError,
    OraLimitError,
    OraValidationError,
    RasterMetadata,
    read_png_metadata,
)

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

# PNG colour types: 0 grey, 2 truecolour, 3 indexed, 4 grey+alpha, 6 RGBA.
COLOUR_GREY, COLOUR_RGB, COLOUR_INDEXED, COLOUR_GREY_ALPHA, COLOUR_RGBA = 0, 2, 3, 4, 6


def chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def png(
    width: int = 4,
    height: int = 3,
    bit_depth: int = 8,
    colour_type: int = COLOUR_RGBA,
    interlace: int = 0,
    *,
    pixel_payload: bytes | None = None,
    signature: bytes = PNG_SIGNATURE,
) -> bytes:
    """A structurally valid PNG. Pixel content is irrelevant to metadata."""
    ihdr = struct.pack(
        ">IIBBBBB", width, height, bit_depth, colour_type, 0, 0, interlace
    )
    body = pixel_payload if pixel_payload is not None else zlib.compress(b"\0" * 16)
    return signature + chunk(b"IHDR", ihdr) + chunk(b"IDAT", body) + chunk(b"IEND", b"")


# ── Metadata comes from the header ─────────────────────────────────────────


def test_metadata_is_read_from_the_header() -> None:
    metadata = read_png_metadata(png(width=640, height=480))

    assert isinstance(metadata, RasterMetadata)
    assert (metadata.width, metadata.height) == (640, 480)
    assert metadata.bit_depth == 8
    assert metadata.colour_type == COLOUR_RGBA


def test_metadata_is_available_even_when_the_pixel_data_is_unreadable() -> None:
    """The proof that metadata is read *before* decode: this file's IDAT is
    garbage that no decoder could inflate, and its dimensions still resolve. A
    reader that decoded pixels to answer "how big is it" would fail here."""
    corrupt = png(width=1024, height=768, pixel_payload=b"\xff\x00 not zlib at all")

    metadata = read_png_metadata(corrupt)

    assert (metadata.width, metadata.height) == (1024, 768)


def test_only_the_header_is_consumed() -> None:
    """A truncated file that still contains a complete IHDR yields metadata --
    further confirmation nothing beyond the header is required."""
    whole = png(width=32, height=32)
    header_only = whole[: len(PNG_SIGNATURE) + 25]

    metadata = read_png_metadata(header_only)

    assert (metadata.width, metadata.height) == (32, 32)


def test_channel_count_and_interlace_are_exposed() -> None:
    assert read_png_metadata(png(colour_type=COLOUR_GREY)).channels == 1
    assert read_png_metadata(png(colour_type=COLOUR_GREY_ALPHA)).channels == 2
    assert read_png_metadata(png(colour_type=COLOUR_RGB)).channels == 3
    assert read_png_metadata(png(colour_type=COLOUR_RGBA)).channels == 4
    assert read_png_metadata(png(colour_type=COLOUR_INDEXED)).channels == 1
    assert read_png_metadata(png(interlace=1)).interlaced is True
    assert read_png_metadata(png(interlace=0)).interlaced is False


# ── Media type: it must actually be a PNG ──────────────────────────────────


@pytest.mark.parametrize(
    "bad_signature",
    [b"\x89PNG\r\n\x1a\x00", b"GIF89a\x00\x00", b"\xff\xd8\xff\xe0JFIF", b"", b"PK\x03\x04"],
    ids=["corrupt-png", "gif", "jpeg", "empty", "zip"],
)
def test_a_non_png_asset_is_refused(bad_signature: bytes) -> None:
    """"validate ... media type" -- the reference says .png, and a JPEG or a
    nested ZIP arriving under a .png name is the interesting case."""
    with pytest.raises(OraValidationError) as raised:
        read_png_metadata(bad_signature + b"whatever follows")

    assert "png" in str(raised.value).lower()


def test_a_file_too_short_to_hold_a_header_is_refused() -> None:
    with pytest.raises(OraValidationError):
        read_png_metadata(PNG_SIGNATURE + b"\x00\x00")


def test_the_first_chunk_must_be_ihdr() -> None:
    """PNG requires IHDR first. A file leading with another chunk is malformed,
    and reading dimensions from wherever IHDR happens to appear would let a
    crafted file disagree with every other decoder."""
    forged = PNG_SIGNATURE + chunk(b"tEXt", b"x") + chunk(
        b"IHDR", struct.pack(">IIBBBBB", 8, 8, 8, COLOUR_RGBA, 0, 0, 0)
    )

    with pytest.raises(OraValidationError) as raised:
        read_png_metadata(forged)

    assert "IHDR" in str(raised.value)


# ── Dimensions and channel depth ───────────────────────────────────────────


@pytest.mark.parametrize("width,height", [(0, 10), (10, 0), (0, 0)])
def test_zero_dimensions_are_refused(width: int, height: int) -> None:
    with pytest.raises(OraValidationError):
        read_png_metadata(png(width=width, height=height))


@pytest.mark.parametrize("bit_depth", [0, 3, 5, 7, 9, 12, 17, 32])
def test_invalid_bit_depths_are_refused(bit_depth: int) -> None:
    """PNG permits only 1, 2, 4, 8 and 16."""
    with pytest.raises(OraValidationError) as raised:
        read_png_metadata(png(bit_depth=bit_depth))

    assert "bit depth" in str(raised.value).lower()


@pytest.mark.parametrize("colour_type", [1, 5, 7, 8, 255])
def test_invalid_colour_types_are_refused(colour_type: int) -> None:
    with pytest.raises(OraValidationError) as raised:
        read_png_metadata(png(colour_type=colour_type))

    assert "colour type" in str(raised.value).lower()


@pytest.mark.parametrize("interlace", [2, 3, 255])
def test_invalid_interlace_methods_are_refused(interlace: int) -> None:
    with pytest.raises(OraValidationError):
        read_png_metadata(png(interlace=interlace))


# ── Declared resource budgets ──────────────────────────────────────────────


def test_an_asset_declaring_an_enormous_surface_is_refused() -> None:
    """A 16-byte file can declare a 40-gigapixel image. That declaration is what
    a caller would allocate against, so it is checked against the budget before
    anything is decoded."""
    limits = ResourceLimits(max_decompressed_bytes=10_000_000)

    with pytest.raises(OraLimitError) as raised:
        read_png_metadata(png(width=200_000, height=200_000), limits=limits)

    assert "budget" in str(raised.value).lower() or "byte" in str(raised.value).lower()


def test_an_ordinary_asset_passes_the_same_budget() -> None:
    """Control: the rejection above must be about the absurd declaration, not
    about the budget being unusably small."""
    limits = ResourceLimits(max_decompressed_bytes=10_000_000)

    metadata = read_png_metadata(png(width=800, height=600), limits=limits)

    assert metadata.width == 800


def test_the_declared_byte_size_accounts_for_depth_and_channels() -> None:
    """16-bit RGBA is eight bytes per pixel, not one; a budget check that
    counted pixels would under-estimate by 8x."""
    metadata = read_png_metadata(png(width=100, height=100, bit_depth=16))

    assert metadata.declared_byte_size == 100 * 100 * 4 * 2


# ── Baseline asset constraints ─────────────────────────────────────────────


def test_a_conforming_thumbnail_is_accepted() -> None:
    metadata = read_png_metadata(png(width=256, height=256, bit_depth=8))

    assert metadata.satisfies_thumbnail_constraints() is True


@pytest.mark.parametrize(
    "kwargs,reason",
    [
        ({"width": 257, "height": 100}, "wider than 256"),
        ({"width": 100, "height": 257}, "taller than 256"),
        ({"bit_depth": 16}, "16 bits per channel"),
        ({"interlace": 1}, "interlaced"),
    ],
)
def test_non_conforming_thumbnails_are_rejected(kwargs: dict, reason: str) -> None:
    """"must be a non-interlaced PNG with 8 bits per channel, and must not
    exceed 256 by 256 pixels." """
    metadata = read_png_metadata(png(**kwargs))

    assert metadata.satisfies_thumbnail_constraints() is False, reason


@pytest.mark.parametrize("bit_depth,expected", [(8, True), (16, True), (1, False), (4, False)])
def test_merged_image_accepts_only_8_or_16_bits(bit_depth: int, expected: bool) -> None:
    """"contains the final rendered image as a PNG with 8 or 16 bits per channel."

    Greyscale is used deliberately: PNG permits 1- and 4-bit samples only for
    greyscale and indexed images, so a 1-bit RGBA file would be rejected as
    malformed before this constraint could ever be evaluated.
    """
    metadata = read_png_metadata(png(bit_depth=bit_depth, colour_type=COLOUR_GREY))

    assert metadata.satisfies_merged_image_constraints() is expected


def test_low_bit_depths_are_rejected_outright_for_truecolour() -> None:
    """The reason the test above uses greyscale, asserted rather than assumed."""
    with pytest.raises(OraValidationError) as raised:
        read_png_metadata(png(bit_depth=1, colour_type=COLOUR_RGBA))

    assert "colour type" in str(raised.value).lower()


# ── Resolving a layer's reference against the archive ──────────────────────


def _archive_with(members: dict[str, bytes], stack_xml: bytes) -> bytes:
    import io
    import zipfile

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        archive.writestr(info, b"image/openraster")
        archive.writestr("stack.xml", stack_xml)
        for name, payload in members.items():
            archive.writestr(name, payload)
    return buffer.getvalue()


STACK_ONE_LAYER = (
    b'<?xml version="1.0" encoding="UTF-8"?>'
    b'<image w="8" h="8" version="0.0.5"><stack>'
    b'<layer name="only" src="data/only.png"/>'
    b"</stack></image>"
)


def test_a_layer_resolves_to_its_raster() -> None:
    from format_factory.ora import OraContainer, parse_stack, resolve_asset

    payload = _archive_with({"data/only.png": png(width=64, height=48)}, STACK_ONE_LAYER)
    container = OraContainer.from_bytes(payload)
    document = parse_stack(container.read("stack.xml"))

    asset = resolve_asset(container, document.root.children[0])

    assert asset.src == "data/only.png"
    assert (asset.metadata.width, asset.metadata.height) == (64, 48)


def test_a_layer_referencing_an_absent_member_is_reported() -> None:
    """"validate existence" -- naming both the layer and the missing member,
    because "file not found" alone is useless in a 200-layer document."""
    from format_factory.ora import OraContainer, parse_stack, resolve_asset

    payload = _archive_with({"data/other.png": png()}, STACK_ONE_LAYER)
    container = OraContainer.from_bytes(payload)
    document = parse_stack(container.read("stack.xml"))

    with pytest.raises(OraValidationError) as raised:
        resolve_asset(container, document.root.children[0])

    assert "only" in str(raised.value) and "data/only.png" in str(raised.value)


def test_asset_lookup_is_case_sensitive() -> None:
    """Case-folding here would make a document render differently depending on
    the filesystem it was extracted on."""
    from format_factory.ora import OraContainer, parse_stack, resolve_asset

    payload = _archive_with({"data/Only.png": png()}, STACK_ONE_LAYER)
    container = OraContainer.from_bytes(payload)
    document = parse_stack(container.read("stack.xml"))

    with pytest.raises(OraValidationError):
        resolve_asset(container, document.root.children[0])


def test_all_assets_resolve_in_visual_order_across_nested_groups() -> None:
    from format_factory.ora import OraContainer, parse_stack, resolve_all_assets

    stack_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<image w="8" h="8" version="0.0.5"><stack>'
        b'<layer name="top" src="data/1.png"/>'
        b'<stack name="group"><layer name="mid" src="data/2.png"/></stack>'
        b'<layer name="bottom" src="data/3.png"/>'
        b"</stack></image>"
    )
    members = {
        "data/1.png": png(width=10, height=10),
        "data/2.png": png(width=20, height=20),
        "data/3.png": png(width=30, height=30),
    }
    container = OraContainer.from_bytes(_archive_with(members, stack_xml))
    document = parse_stack(container.read("stack.xml"))

    assets = resolve_all_assets(container, document.root)

    assert [asset.metadata.width for asset in assets] == [10, 20, 30]


def test_resolution_fails_on_the_first_missing_layer_rather_than_returning_part() -> None:
    """A document missing one layer is not renderable; returning most of it
    invites a caller to render a wrong image and never notice."""
    from format_factory.ora import OraContainer, parse_stack, resolve_all_assets

    stack_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<image w="8" h="8" version="0.0.5"><stack>'
        b'<layer name="present" src="data/1.png"/>'
        b'<layer name="absent" src="data/2.png"/>'
        b"</stack></image>"
    )
    container = OraContainer.from_bytes(
        _archive_with({"data/1.png": png()}, stack_xml)
    )
    document = parse_stack(container.read("stack.xml"))

    with pytest.raises(OraValidationError):
        resolve_all_assets(container, document.root)
