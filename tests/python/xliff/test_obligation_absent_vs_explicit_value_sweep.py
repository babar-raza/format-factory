"""XLIFF-PRESERVE-001 against the shipped namespace.

MUST (SAL-XLIFF-OBL-612349C06EB3E809): "Preserve the distinction between
an absent optional value and an explicitly written default or empty
value."

Before this slice: only Note.priority had been directly verified (an
absent priority attribute leaves Note.priority as None, distinguishable
from an explicit numeric value, because reader.py checks presence before
parsing rather than defaulting). The obligation's own finding named this
as one instance of a broader pattern never systematically checked: "a
systematic sweep of every other optional field's absent-vs-explicit-
default handling (segment/@state empty-string normalization, other
note/unit attributes) has not been done."

This file performs that sweep, grounded directly in the pinned XLIFF 2.1
specification's own per-attribute "Value description" / "Default value"
entries (read from .local/format-contracts/acquired/xliff/src-xliff-001.bin
section 4.3.1), rather than assuming every field behaves like priority:

- Segment.state: the spec constrains state to exactly {initial,
  translated, reviewed, final} -- none of which is the empty string -- so
  reader.py's `element.get("state", "")` is safe: "" can only ever mean
  "absent" in a conformant document. Proven directly.
- Segment.sub_state: the spec requires subState's value to always contain
  a ':' separator (prefix:sub-value) -- again, "" can never be a valid
  explicit value. Proven directly.
- Note.applies_to: the spec constrains appliesTo to exactly {source,
  target} -- same reasoning, "" is unambiguous. Proven directly.
- XliffDocument.target_language: reader.py uses `root.get("trgLang")`
  with NO default, so absent is None and any explicit value (even one
  that happened to be syntactically odd) is a distinct non-None string.
  Proven directly.
- Note.category: genuinely different from the above four. The spec's own
  entry reads "Value description: Text. Default value: undefined" -- no
  enum, no format constraint. An explicitly empty category attribute
  (category="") IS syntactically valid free text, distinct in meaning
  from the attribute being absent entirely, but this package's Note.category
  defaults to "" for both cases -- reader.py's `note.get("category", "")`
  collapses them. This is confirmed here as a genuine, narrow remaining
  gap (not force-closed): fixing it would mean changing Note.category's
  type from `str` to `str | None`, a public-API type change out of scope
  for this slice, deliberately left for its own dedicated investigation.
"""

from __future__ import annotations

from format_factory.xliff import dumps, loads

_NS = "urn:oasis:names:tc:xliff:document:2.0"


def _document(unit_body: str, *, target_language: str = "") -> bytes:
    trg = f' trgLang="{target_language}"' if target_language else ""
    return (
        f'<xliff xmlns="{_NS}" version="2.1" srcLang="en"{trg}>'
        f'<file id="f1">{unit_body}</file></xliff>'
    ).encode()


def _segment(source_body: str = "hi") -> str:
    return f'<unit id="u1"><segment id="s1"><source>{source_body}</source></segment></unit>'


def test_segment_state_absent_is_distinguishable_from_explicit_initial() -> None:
    """The spec's own state attribute entry restricts values to exactly
    {initial, translated, reviewed, final} -- "" is never a valid explicit
    value, so absent and explicit-"initial" are safely distinguishable
    even though both eventually mean "the default"."""
    absent = loads(_document(_segment())).files[0].children[0].segments[0]
    explicit = loads(
        _document('<unit id="u1"><segment id="s1" state="initial"><source>hi</source></segment></unit>')
    ).files[0].children[0].segments[0]

    assert absent.state == ""
    assert explicit.state == "initial"
    assert absent.state != explicit.state


def test_segment_sub_state_absent_is_distinguishable_from_any_explicit_value() -> None:
    """subState's own spec entry requires the value to always contain a
    ':' separator (prefix:sub-value) -- "" can never be a valid explicit
    value, so absence is unambiguous."""
    absent = loads(_document(_segment())).files[0].children[0].segments[0]
    xml = (
        '<unit id="u1"><segment id="s1" state="translated" subState="xlf:reviewed">'
        "<source>hi</source><target>hej</target></segment></unit>"
    )
    explicit = loads(_document(xml)).files[0].children[0].segments[0]

    assert absent.sub_state == ""
    assert explicit.sub_state == "xlf:reviewed"
    assert absent.sub_state != explicit.sub_state


def test_note_applies_to_absent_is_distinguishable_from_explicit_source() -> None:
    """appliesTo's own spec entry restricts values to exactly {source,
    target} -- "" is never a valid explicit value."""
    absent_xml = '<unit id="u1"><notes><note>plain</note></notes>' + _segment().split(">", 1)[1]
    explicit_xml = (
        '<unit id="u1"><notes><note appliesTo="source">plain</note></notes>'
        + _segment().split(">", 1)[1]
    )

    absent = loads(_document(absent_xml)).files[0].children[0].notes[0]
    explicit = loads(_document(explicit_xml)).files[0].children[0].notes[0]

    assert absent.applies_to == ""
    assert explicit.applies_to == "source"
    assert absent.applies_to != explicit.applies_to


def test_target_language_absent_is_none_not_an_empty_string() -> None:
    """reader.py's root.get("trgLang") carries no default -- absent is
    None, never conflated with any string value, even an empty one a
    hostile document might supply."""
    absent = loads(_document(_segment()))
    explicit = loads(_document(_segment(), target_language="fr"))

    assert absent.target_language is None
    assert explicit.target_language == "fr"


def test_note_category_absent_is_distinguishable_from_explicit_empty() -> None:
    """category is unconstrained free text per the spec ("Value
    description: Text. Default value: undefined"), so an explicit
    category="" is syntactically legitimate and semantically distinct from
    the attribute being absent. Note.category is now str | None (was str,
    defaulting both cases to ""): reader.py's note.get("category") returns
    None when the attribute is absent and "" when it is explicitly empty,
    the same distinguishing pattern already proven for Note.priority."""
    absent_xml = '<unit id="u1"><notes><note>plain</note></notes>' + _segment().split(">", 1)[1]
    explicit_empty_xml = (
        '<unit id="u1"><notes><note category="">plain</note></notes>'
        + _segment().split(">", 1)[1]
    )

    absent = loads(_document(absent_xml)).files[0].children[0].notes[0]
    explicit_empty = loads(_document(explicit_empty_xml)).files[0].children[0].notes[0]

    assert absent.category is None
    assert explicit_empty.category == ""
    assert absent.category != explicit_empty.category


def test_note_explicit_empty_category_survives_a_write_reload_round_trip() -> None:
    """The writer previously used `if value.category:` (falsy check), which
    dropped an explicit category="" on write -- indistinguishable from
    never having one. Confirmed fixed: `if value.category is not None:`
    writes the attribute whenever it is not None, including when it is an
    explicit empty string."""
    explicit_empty_xml = (
        '<unit id="u1"><notes><note category="">plain</note></notes>'
        + _segment().split(">", 1)[1]
    )

    document = loads(_document(explicit_empty_xml))
    reloaded = loads(dumps(document).encode())

    assert reloaded.files[0].children[0].notes[0].category == ""


def test_note_absent_category_stays_absent_through_a_write_reload_round_trip() -> None:
    absent_xml = '<unit id="u1"><notes><note>plain</note></notes>' + _segment().split(">", 1)[1]

    document = loads(_document(absent_xml))
    reloaded = loads(dumps(document).encode())

    assert reloaded.files[0].children[0].notes[0].category is None
