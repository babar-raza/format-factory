"""NRRD-PRESERVE-001 against the shipped namespace.

MUST (SAL-NRRD-OBL-ADAC45BDF110C59C): "Preserve the distinction between an
absent optional value and an explicitly written default or empty value."

Before this slice, this obligation's own implemented_behavior already noted
the distinction was preserved LEXICALLY: `self.header` (a plain
`dict[str, str]`) never loses a present field or invents an absent one. The
obligation's own missing_behavior named two remaining, more specific gaps:
"typed defaults" and "empty values" were not modeled, so a caller had no
first-class way to ask the question -- only some typed accessors (content,
min, max, ...) happened to return `None` for absence via their own internal
`.get()` call; others (spacings, axis mins, labels, kinds, ...) collapse
BOTH "never declared" and "declared as literally empty" into the same `[]`
return value, indistinguishable from outside; and a defaulted scalar field
like `encoding` (falls back to "raw" when absent, per NRRD's own baseline
default) cannot be told apart from a document that explicitly wrote
`encoding: raw` -- both currently look identical to a caller.

`NrrdDocument.field_present(name)` closes both: `name in self.header` is
exactly the same `name in self.header` idiom `version_requirements()` and
`per_axis_field_arities()` already use internally, now exposed directly so
any caller can ask the presence question for any field without reaching into
the raw header dict themselves -- covering the "empty value" case (a
list-shaped field declared with no tokens) and the "typed default" case
(a scalar field silently defaulted vs explicitly written) uniformly, since
NRRD's own wire format has no separate default-marker mechanism beyond
presence itself: any string written to a header key IS an explicit write,
whatever it happens to equal.
"""

from __future__ import annotations

import pytest

from format_factory.nrrd import NrrdDocument, NrrdWriteError, dumps, loads


def _document(header: dict[str, str], array: list[int] | None = None) -> NrrdDocument:
    return NrrdDocument.from_mapping(
        {
            "version": 4,
            "header": header,
            "array": array or [],
        }
    )


# ── Absence vs presence, scalar fields already returning None on absence ──


def test_an_absent_scalar_field_is_reported_as_not_present() -> None:
    document = _document({"type": "uint8", "dimension": "1", "sizes": "1"})

    assert document.field_present("content") is False
    assert document.content is None


def test_a_present_scalar_field_is_reported_as_present_even_when_its_value_is_empty() -> None:
    """Only reachable via `from_mapping()`, not through a real file's own
    text -- the header grammar itself refuses a syntactically empty value
    (see the writer-refusal tests below), but the in-memory model can still
    represent this state, and `field_present` still answers correctly."""
    document = _document({"type": "uint8", "dimension": "1", "sizes": "1", "content": ""})

    assert document.field_present("content") is True
    assert document.content == ""


# ── The writer refuses to produce output it could not read back ────────────


def test_writing_a_document_with_an_explicitly_empty_scalar_field_is_refused() -> None:
    """`_header_bytes` mirrors the reader's own `not value.strip()`
    refusal rather than silently emitting `content: ` -- a line the same
    reader would then reject as malformed on read-back."""
    document = _document(
        {"type": "uint8", "dimension": "1", "sizes": "1", "encoding": "raw", "content": ""},
        array=[0],
    )

    with pytest.raises(NrrdWriteError, match="empty value"):
        dumps(document)


def test_writing_a_document_with_an_explicitly_empty_per_axis_field_is_refused() -> None:
    document = _document(
        {"type": "uint8", "dimension": "1", "sizes": "1", "encoding": "raw", "spacings": ""},
        array=[0],
    )

    with pytest.raises(NrrdWriteError, match="empty value"):
        dumps(document)


# ── Absence vs presence, list-shaped fields that collapse to [] either way ──


def test_an_absent_per_axis_field_is_not_present_even_though_the_typed_accessor_returns_empty() -> None:
    document = _document({"type": "uint8", "dimension": "1", "sizes": "1"})

    assert document.field_present("spacings") is False
    assert document.spacings == []


def test_a_per_axis_field_declared_empty_is_present_even_though_the_typed_accessor_also_returns_empty() -> None:
    """The two cases are indistinguishable via `.spacings` alone (both `[]`)
    -- `field_present` is what tells them apart."""
    document = _document({"type": "uint8", "dimension": "1", "sizes": "1", "spacings": ""})

    assert document.field_present("spacings") is True
    assert document.spacings == []


# ── Silent default vs explicit write of the same value ─────────────────────


def test_a_defaulted_scalar_is_not_present_even_though_the_typed_accessor_returns_the_default() -> None:
    document = _document({"type": "uint8", "dimension": "1", "sizes": "1"})

    assert document.field_present("encoding") is False
    assert document.encoding == "raw"


def test_an_explicitly_written_default_value_is_present_and_indistinguishable_in_value_alone() -> None:
    """Both documents report `.encoding == "raw"`; only `field_present`
    reveals that this one actually wrote it."""
    document = _document(
        {"type": "uint8", "dimension": "1", "sizes": "1", "encoding": "raw"}
    )

    assert document.field_present("encoding") is True
    assert document.encoding == "raw"


# ── The distinction survives a full write/read round trip ──────────────────


def test_presence_and_absence_both_survive_a_write_read_round_trip() -> None:
    """The header grammar itself refuses a syntactically empty value
    (`value.strip()` must be non-empty -- codec/reader/reader.py's own
    `_parse_header`), so an explicitly-empty field is only reachable via
    `from_mapping()`, not through a real file's own text; this proves the
    presence/absence distinction survives round-tripping THROUGH the real
    file grammar for a field that legitimately carries a non-empty value."""
    header = "NRRD0004\ntype: uint8\ndimension: 1\nsizes: 1\nencoding: raw\ncontent: a description\n\n"
    original = loads(header.encode() + b"\x01")
    assert original.field_present("content") is True
    assert original.field_present("space") is False

    reloaded = loads(dumps(original))

    assert reloaded.field_present("content") is True
    assert reloaded.field_present("space") is False
