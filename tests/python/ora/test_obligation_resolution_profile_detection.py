"""ORA-RESOLUTION-001 against the shipped namespace.

MUST: "Model paired positive horizontal and vertical resolution values,
distinguish absent values from defaults, and enforce the profiles in which
resolution is defined."

"(Layer Stack -- image element) Since profile 0.0.3, xres and yres are
optional positive integer pixels-per-inch values that must be specified
together and default to 72."

required_tests: "Absent/default/pairing/minimum/profile-boundary round trips."

Scope of this file: the one piece of the two obligations above with no
dedicated test until now -- "enforce the profiles in which resolution is
defined", i.e. that a non-default resolution alone (no isolation feature
used) is detected as profile 0.0.3, distinctly from the 0.0.4 (isolation)
and 0.0.2 (mergedimage-only) cases already covered elsewhere. "Paired
positive values", "absent values default to 72", and "must be specified
together" are proven at the parser/model level in
test_obligation_stack_and_document.py and
test_obligation_document_model_construction.py; this file does not repeat
that coverage, only the profile-detection half.
"""

from __future__ import annotations

import io
import struct
import zipfile
import zlib

from format_factory.ora import load

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _png(width: int = 8, height: int = 8) -> bytes:
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (
        PNG_SIGNATURE
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(b"\0" * 16))
        + chunk(b"IEND", b"")
    )


def _archive(stack_xml: bytes) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        zf.writestr(info, b"image/openraster")
        zf.writestr("stack.xml", stack_xml)
        zf.writestr("Thumbnails/thumbnail.png", _png(16, 16))
        zf.writestr("mergedimage.png", _png())
        zf.writestr("data/only.png", _png())
    return buffer.getvalue()


def test_non_default_resolution_alone_is_detected_as_profile_0_0_3() -> None:
    """No isolation feature is used here, so the 0.0.4 trigger cannot fire --
    isolating the resolution trigger from the isolation trigger this package's
    own _detect_version checks first."""
    stack_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<image w="8" h="8" version="0.0.1" xres="300" yres="300">'
        b'<stack><layer name="only" src="data/only.png"/></stack>'
        b"</image>"
    )
    image = load(_archive(stack_xml))

    assert image.declared_version == "0.0.1"
    assert image.detected_version == "0.0.3"
    assert image.declared_version != image.detected_version


def test_resolution_trigger_outranks_the_mergedimage_only_trigger() -> None:
    """mergedimage.png is present in every archive this file builds (it is a
    baseline-asset requirement, not a profile feature), so the 0.0.2 trigger
    alone would report 0.0.2 -- non-default resolution must still win."""
    stack_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<image w="8" h="8" version="0.0.1" xres="150" yres="150">'
        b'<stack><layer name="only" src="data/only.png"/></stack>'
        b"</image>"
    )
    image = load(_archive(stack_xml))

    assert image.detected_version == "0.0.3"


def test_declaring_0_0_3_with_non_default_resolution_has_no_version_drift() -> None:
    stack_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<image w="8" h="8" version="0.0.3" xres="96" yres="96">'
        b'<stack><layer name="only" src="data/only.png"/></stack>'
        b"</image>"
    )
    image = load(_archive(stack_xml))

    assert image.declared_version == image.detected_version == "0.0.3"


def test_default_resolution_alone_does_not_trigger_0_0_3() -> None:
    """Control: detection must not report 0.0.3 unconditionally whenever xres/
    yres are present in the model -- only when they differ from the spec
    default of 72, since an explicit xres="72" yres="72" is indistinguishable
    from the default at the model layer by design (see document.py's own
    docstring: "there is no absent/present distinction left to validate
    here" once construction succeeds)."""
    stack_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<image w="8" h="8" version="0.0.1" xres="72" yres="72">'
        b'<stack><layer name="only" src="data/only.png"/></stack>'
        b"</image>"
    )
    image = load(_archive(stack_xml))

    assert image.detected_version == "0.0.2"  # mergedimage.png is present
