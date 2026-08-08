"""ORA-BASELINEASSET-001 (SAL-ORA-OBL-52746ABC41B3E790) against the shipped
namespace.

MUST: "Read, validate, generate, and replace required thumbnail and
flattened-view assets without confusing them with editable layer sources."

"Read" and "validate" were already implemented (_baseline_asset_diagnostics,
read_png_metadata, satisfies_thumbnail_constraints/satisfies_merged_image_
constraints) and "without confusing them with editable layer sources" was
already proven (thumbnail/merged-image checks are a code path entirely
separate from layer src resolution). This obligation's own missing_behavior
named "generate" and "replace" together as absent, but they are not the
same requirement: "generate" needs actual pixel-compositing/downscaling
computation this package has no rendering engine for at all (the same
genuinely blocked scope as ORA-RENDER-001); "replace" does not -- it only
needs to accept a caller-supplied new asset (produced by some other means)
and validate it the same way a freshly loaded document's own assets are
validated, then swap it in.

replace_baseline_asset() (lifecycle.py) closes the "replace" half: it
reuses read_png_metadata and the exact same
satisfies_thumbnail_constraints()/satisfies_merged_image_constraints()
checks _baseline_asset_diagnostics already applies on load, refusing a
non-conforming replacement rather than silently accepting it, and returns
a new OraImage (via dataclasses.replace, non-mutating) with the member
swapped. "Generate" remains this obligation's own sole, honestly
unresolved gap.
"""

from __future__ import annotations

import io
import struct
import zipfile
import zlib

import pytest

from format_factory.ora import (
    OraValidationError,
    dumps,
    load,
    loads,
    replace_baseline_asset,
)

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload))
        + kind
        + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def _png(
    width: int = 8, height: int = 8, bit_depth: int = 8, colour_type: int = 6, interlace: int = 0
) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, bit_depth, colour_type, 0, 0, interlace)
    return (
        PNG_SIGNATURE
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(b"\0" * 16))
        + _chunk(b"IEND", b"")
    )


_STACK = (
    b'<?xml version="1.0" encoding="UTF-8"?>\n'
    b'<image w="8" h="8" version="0.0.5">'
    b'<stack><layer name="only" src="data/only.png"/></stack>'
    b"</image>"
)


def _archive(*, thumbnail: bytes, merged: bytes) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        zf.writestr(info, b"image/openraster")
        zf.writestr("stack.xml", _STACK)
        zf.writestr("data/only.png", _png())
        zf.writestr("Thumbnails/thumbnail.png", thumbnail)
        zf.writestr("mergedimage.png", merged)
    return buffer.getvalue()


def _complete_image():
    payload = _archive(thumbnail=_png(64, 64), merged=_png(8, 8))
    return load(payload)


# -- Swapping a conforming replacement in --------------------------------


def test_replace_baseline_asset_swaps_the_thumbnail_member() -> None:
    image = _complete_image()
    new_thumbnail = _png(100, 100)

    replaced = replace_baseline_asset(image, thumbnail=new_thumbnail)

    assert replaced.members["Thumbnails/thumbnail.png"] == new_thumbnail


def test_replace_baseline_asset_swaps_the_merged_image_member() -> None:
    image = _complete_image()
    new_merged = _png(16, 16, bit_depth=16)

    replaced = replace_baseline_asset(image, merged_image=new_merged)

    assert replaced.members["mergedimage.png"] == new_merged


def test_replace_baseline_asset_can_replace_both_in_one_call() -> None:
    image = _complete_image()
    new_thumbnail = _png(200, 200)
    new_merged = _png(32, 32, bit_depth=16)

    replaced = replace_baseline_asset(image, thumbnail=new_thumbnail, merged_image=new_merged)

    assert replaced.members["Thumbnails/thumbnail.png"] == new_thumbnail
    assert replaced.members["mergedimage.png"] == new_merged


def test_replace_baseline_asset_does_not_mutate_the_original_image() -> None:
    image = _complete_image()
    original_thumbnail = image.members["Thumbnails/thumbnail.png"]

    replace_baseline_asset(image, thumbnail=_png(50, 50))

    assert image.members["Thumbnails/thumbnail.png"] == original_thumbnail


# -- Refusing a non-conforming replacement, not silently accepting it -----


def test_replace_baseline_asset_refuses_an_oversized_thumbnail() -> None:
    image = _complete_image()

    with pytest.raises(OraValidationError, match="256x256"):
        replace_baseline_asset(image, thumbnail=_png(300, 300))


def test_replace_baseline_asset_refuses_an_interlaced_thumbnail() -> None:
    image = _complete_image()

    with pytest.raises(OraValidationError, match="256x256"):
        replace_baseline_asset(image, thumbnail=_png(64, 64, interlace=1))


def test_replace_baseline_asset_refuses_a_wrong_bit_depth_merged_image() -> None:
    image = _complete_image()

    with pytest.raises(OraValidationError, match="8 or 16 bits"):
        replace_baseline_asset(image, merged_image=_png(8, 8, bit_depth=4, colour_type=3))


def test_replace_baseline_asset_requires_at_least_one_replacement() -> None:
    image = _complete_image()

    with pytest.raises(OraValidationError, match="at least one"):
        replace_baseline_asset(image)


# -- The replaced asset round-trips through the full write/read cycle -----


def test_the_replaced_thumbnail_round_trips_through_dumps_and_reload() -> None:
    image = _complete_image()
    new_thumbnail = _png(120, 120)

    replaced = replace_baseline_asset(image, thumbnail=new_thumbnail)
    reloaded = loads(dumps(replaced))

    assert reloaded.members["Thumbnails/thumbnail.png"] == new_thumbnail
