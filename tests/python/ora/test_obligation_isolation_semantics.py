"""ORA-ISOLATION-001 against the shipped namespace.

MUST: "Model declared and inferred group isolation separately, enforce
profile availability, and render isolated groups against a transparent
intermediate backdrop."

"(Layer Stack — Compositing the image) Since profile 0.0.4, a non-root
stack is isolated when isolation is isolate, opacity is below one, or
composite-op differs from svg:src-over."

required_tests: "Declared/inferred isolation pixel vectors and pre-profile
rejection/preservation cases."

Scope of this file: the two halves of "model declared and inferred group
isolation separately" (OraStack.is_isolated_group) and "enforce profile
availability" (the declared-vs-detected version separation this package
already uses for exactly this purpose) -- both already implemented, neither
with a dedicated test until now. "Render isolated groups against a
transparent intermediate backdrop" is actual pixel compositing this package
has no rendering engine for at all; not attempted here, and not claimed.
"""

from __future__ import annotations

import io
import zipfile

from format_factory.ora import OraStack, ReadMode, load, loads
from format_factory.ora.model.stack import DEFAULT_COMPOSITE_OP

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _png(width: int = 8, height: int = 8) -> bytes:
    import struct
    import zlib

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


# ── Declared isolation: the "isolation" attribute ───────────────────────────


def test_declared_isolate_makes_a_stack_isolated() -> None:
    stack = OraStack(isolation="isolate")

    assert stack.is_isolated_group is True


def test_declared_auto_alone_is_not_isolated() -> None:
    stack = OraStack(isolation="auto")

    assert stack.is_isolated_group is False


def test_isolation_defaults_to_auto_and_is_not_isolated() -> None:
    stack = OraStack()

    assert stack.isolation == "auto"
    assert stack.is_isolated_group is False


# ── Inferred isolation: opacity below one ───────────────────────────────────


def test_opacity_below_one_infers_isolation_even_without_the_attribute() -> None:
    """"a non-root stack is isolated when isolation is isolate, opacity is
    below one, or composite-op differs from svg:src-over." Three independent
    triggers -- this is the opacity one, with isolation left at its default."""
    stack = OraStack(opacity=0.5)

    assert stack.isolation == "auto"
    assert stack.is_isolated_group is True


def test_opacity_of_exactly_one_does_not_infer_isolation() -> None:
    stack = OraStack(opacity=1.0)

    assert stack.is_isolated_group is False


# ── Inferred isolation: composite-op differing from the default ────────────


def test_non_default_composite_op_infers_isolation() -> None:
    stack = OraStack(composite_op="svg:multiply")

    assert stack.is_isolated_group is True


def test_default_composite_op_does_not_infer_isolation() -> None:
    stack = OraStack(composite_op=DEFAULT_COMPOSITE_OP)

    assert stack.is_isolated_group is False


# ── Declared and inferred are modeled separately, not conflated ─────────────


def test_declared_and_inferred_isolation_are_distinguishable() -> None:
    """"Model declared and inferred group isolation separately" -- a caller
    can tell WHY a stack is isolated, not only THAT it is."""
    declared_only = OraStack(isolation="isolate", opacity=1.0, composite_op=DEFAULT_COMPOSITE_OP)
    inferred_only = OraStack(isolation="auto", opacity=0.4)

    assert declared_only.isolation == "isolate"
    assert declared_only.is_isolated_group is True
    assert inferred_only.isolation == "auto"
    assert inferred_only.is_isolated_group is True


def test_neither_declared_nor_inferred_is_not_isolated() -> None:
    stack = OraStack(isolation="auto", opacity=1.0, composite_op=DEFAULT_COMPOSITE_OP)

    assert stack.is_isolated_group is False


# ── Parsing a real document: isolation survives structurally ───────────────


def test_isolation_attribute_parses_from_real_stack_xml() -> None:
    stack_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<image w="8" h="8" version="0.0.5">'
        b'<stack><stack name="group" isolation="isolate">'
        b'<layer name="only" src="data/only.png"/>'
        b"</stack></stack></image>"
    )
    image = load(_archive(stack_xml))

    nested = image.document.root.children[0]
    assert isinstance(nested, OraStack)
    assert nested.isolation == "isolate"
    assert nested.is_isolated_group is True


def test_nested_stack_isolation_is_evaluated_per_stack_not_inherited() -> None:
    """A non-isolated group nested inside an isolated one keeps its own,
    independent isolation state -- isolation is a per-stack attribute/
    inference, not something a parent silently imposes on its children."""
    stack_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<image w="8" h="8" version="0.0.5">'
        b'<stack><stack name="outer" isolation="isolate">'
        b'<stack name="inner" isolation="auto">'
        b'<layer name="only" src="data/only.png"/>'
        b"</stack></stack></stack></image>"
    )
    image = load(_archive(stack_xml))

    outer = image.document.root.children[0]
    inner = outer.children[0]
    assert outer.is_isolated_group is True
    assert inner.is_isolated_group is False


# ── Profile availability: declared vs. detected version separation ─────────


def test_isolation_usage_is_detected_as_profile_0_0_4() -> None:
    """"enforce profile availability": isolation semantics apply only from
    profile 0.0.4. This package does not hard-reject an older-declared
    document using isolation (the same declared/detected separation already
    used for xres/yres profile drift), but it DOES make the drift visible --
    the developer_use_case is "without... profile ambiguity", and that
    ambiguity is resolved by exposing both versions rather than picking one."""
    stack_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<image w="8" h="8" version="0.0.1">'
        b'<stack><stack name="group" isolation="isolate">'
        b'<layer name="only" src="data/only.png"/>'
        b"</stack></stack></image>"
    )
    image = load(_archive(stack_xml))

    assert image.declared_version == "0.0.1"
    assert image.detected_version == "0.0.4"
    assert image.declared_version != image.detected_version


def test_inferred_isolation_via_opacity_is_also_detected_as_0_0_4() -> None:
    stack_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<image w="8" h="8" version="0.0.1">'
        b'<stack><stack name="group" opacity="0.5">'
        b'<layer name="only" src="data/only.png"/>'
        b"</stack></stack></image>"
    )
    image = load(_archive(stack_xml))

    assert image.detected_version == "0.0.4"


def test_a_document_declaring_0_0_4_with_isolation_has_no_version_drift() -> None:
    stack_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<image w="8" h="8" version="0.0.4">'
        b'<stack><stack name="group" isolation="isolate">'
        b'<layer name="only" src="data/only.png"/>'
        b"</stack></stack></image>"
    )
    image = load(_archive(stack_xml), mode=ReadMode.TOLERANT)

    assert image.declared_version == image.detected_version == "0.0.4"


def test_a_document_using_no_isolation_features_detects_as_baseline() -> None:
    """Control: detection must not report 0.0.4 unconditionally."""
    stack_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>\n'
        b'<image w="8" h="8" version="0.0.1">'
        b'<stack><layer name="only" src="data/only.png"/></stack>'
        b"</image>"
    )
    image = load(_archive(stack_xml))

    assert image.detected_version == "0.0.2"  # mergedimage.png is present
