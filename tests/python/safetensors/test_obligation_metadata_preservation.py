"""SAFETENSORS-PRESERVE-001 against the shipped namespace.

MUST: "Preserve string file metadata, optional metadata absence, and safe
unknown tensor descriptor fields in preservation mode; reject values that
cannot be represented safely."

required_tests (shared across this capability's 12 obligations): "Unknown
descriptor fields, metadata absence, empty metadata, and string-map round
trips."

Unknown-descriptor-field preservation was already proven (unattributed)
by test_production_namespace.py::test_unknown_tensor_fields_preserved.
String-map validation (metadata values must be strings) was already
proven by test_metadata_must_be_strings. The genuine gap this file closes:
"no __metadata__ key" and "__metadata__: {}" both collapsed to the same
thing (`document.metadata == {}`) everywhere in the pipeline -- the reader
discarded the distinction at parse time (`header.pop("__metadata__", {})`),
so it could never survive a round trip. Fixed by threading a
`metadata_declared` flag through the reader, model, and writer, so a
document that never had a metadata section stays that way after
dumps()/loads(), and a document with an explicit-but-empty section does
too -- distinctly.
"""

from __future__ import annotations

import json
import struct

from format_factory.safetensors import (
    DType,
    SafeTensorsDocument,
    TensorDescriptor,
    dumps,
    loads,
    read_header,
)


def make_file(header: dict[str, object], payload: bytes = b"") -> bytes:
    raw = json.dumps(header, separators=(",", ":")).encode()
    return struct.pack("<Q", len(raw)) + raw + payload


def _tensor() -> dict[str, object]:
    return {"x": {"dtype": "U8", "shape": [1], "data_offsets": [0, 1]}}


# ── Reading: absence vs explicit-empty are distinguishable ──────────────────


def test_absent_metadata_section_is_not_declared() -> None:
    raw = make_file(_tensor(), b"\x01")

    with loads(raw) as document:
        assert document.metadata == {}
        assert document.metadata_declared is False


def test_explicit_empty_metadata_section_is_declared() -> None:
    header = {"__metadata__": {}, **_tensor()}
    raw = make_file(header, b"\x01")

    with loads(raw) as document:
        assert document.metadata == {}
        assert document.metadata_declared is True


def test_non_empty_metadata_is_declared() -> None:
    header = {"__metadata__": {"format": "pt"}, **_tensor()}
    raw = make_file(header, b"\x01")

    with loads(raw) as document:
        assert dict(document.metadata) == {"format": "pt"}
        assert document.metadata_declared is True


# ── read_header (no payload opened) sees the same distinction ─────────────


def test_read_header_reports_absent_metadata() -> None:
    raw = make_file(_tensor(), b"\x01")

    header = read_header(raw)

    assert header.metadata == {}
    assert header.metadata_declared is False


def test_read_header_reports_explicit_empty_metadata() -> None:
    header_dict = {"__metadata__": {}, **_tensor()}
    raw = make_file(header_dict, b"\x01")

    header = read_header(raw)

    assert header.metadata == {}
    assert header.metadata_declared is True


# ── Writing: the distinction survives a round trip ──────────────────────────


def test_absence_round_trips_as_absence() -> None:
    raw = make_file(_tensor(), b"\x01")
    with loads(raw) as document:
        rebuilt = dumps(document)

    assert b"__metadata__" not in rebuilt
    with loads(rebuilt) as reloaded:
        assert reloaded.metadata_declared is False


def test_explicit_empty_round_trips_as_explicit_empty() -> None:
    header = {"__metadata__": {}, **_tensor()}
    raw = make_file(header, b"\x01")
    with loads(raw) as document:
        rebuilt = dumps(document)

    assert b'"__metadata__":{}' in rebuilt
    with loads(rebuilt) as reloaded:
        assert reloaded.metadata == {}
        assert reloaded.metadata_declared is True


def test_non_empty_metadata_round_trips_unaffected() -> None:
    header = {"__metadata__": {"framework": "pytorch"}, **_tensor()}
    raw = make_file(header, b"\x01")
    with loads(raw) as document:
        rebuilt = dumps(document)

    with loads(rebuilt) as reloaded:
        assert dict(reloaded.metadata) == {"framework": "pytorch"}
        assert reloaded.metadata_declared is True


# ── Direct construction: the same rule applies without going through I/O ──


def test_constructing_without_a_metadata_argument_defaults_to_not_declared() -> None:
    document = SafeTensorsDocument(
        tensors={"x": TensorDescriptor("x", DType.U8, (1,), (0, 1))},
        payload=b"\x01",
    )

    assert document.metadata_declared is False
    assert dumps(document).find(b"__metadata__") == -1


def test_constructing_with_an_explicit_empty_mapping_is_declared() -> None:
    document = SafeTensorsDocument(
        tensors={"x": TensorDescriptor("x", DType.U8, (1,), (0, 1))},
        metadata={},
        payload=b"\x01",
    )

    assert document.metadata_declared is True
    assert b'"__metadata__":{}' in dumps(document)


def test_metadata_declared_override_takes_precedence() -> None:
    """The explicit override escape hatch: a caller can force declared=True
    even when passing metadata=None, for constructing test fixtures or
    programmatic documents that should carry an empty section."""
    document = SafeTensorsDocument(
        tensors={"x": TensorDescriptor("x", DType.U8, (1,), (0, 1))},
        metadata=None,
        metadata_declared=True,
        payload=b"\x01",
    )

    assert document.metadata_declared is True
    assert b'"__metadata__":{}' in dumps(document)
