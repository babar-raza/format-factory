"""XLIFF-PARSE-001 -- "ignorable" elements and the unit cardinality
constraint, exercised through the real reader/writer, not just direct
model construction.

MUST (SAL-XLIFF-OBL-194AC86AD7F54920, SAL-XLIFF-OBL-6216215A0A7D5A20;
"OASIS XLIFF 2.0 - unit and segment elements" / "XLIFF core - segment and
ignorable"): "A unit contains at least one segment or ignorable child; each
segment and ignorable contains exactly one source followed by at most one
target" / "unit elements contain segment and ignorable elements whose source
children carry translatable text and whose target children carry
translations."

Before this slice: the reader and model already fully supported
kind="ignorable" (confirmed by reading codec/reader/reader.py directly --
_parse_unit accepts <ignorable> exactly like <segment>, and _parse_segment
sets kind from the element's own local tag name), and validator.py already
enforced "a unit must contain at least one segment or ignorable" (added at
an earlier tick this session for a different, model-level obligation pair).
Neither was exercised by any shipped-namespace test at the loads()/dumps()
level for XLIFF-PARSE-001 specifically.
"""

from __future__ import annotations

from format_factory.xliff import (
    flatten_inline_content,
    loads,
    validate,
)

NAMESPACE = "urn:oasis:names:tc:xliff:document:2.0"


def _document(unit_body: str) -> bytes:
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<xliff xmlns="{NAMESPACE}" version="2.1" srcLang="en" trgLang="fr">'
        f'<file id="f1"><unit id="u1">{unit_body}</unit></file>'
        f"</xliff>"
    ).encode()


def test_an_ignorable_element_parses_with_kind_ignorable() -> None:
    document = loads(
        _document(
            '<ignorable id="i1"><source>  </source><target>  </target></ignorable>'
        )
    )

    unit = next(document.iter_units())
    assert len(unit.segments) == 1
    assert unit.segments[0].kind == "ignorable"
    assert unit.segments[0].id == "i1"


def test_ignorable_source_and_target_carry_text() -> None:
    document = loads(
        _document(
            '<ignorable id="i1"><source>whitespace-ish</source>'
            "<target>espace</target></ignorable>"
        )
    )

    ignorable = next(document.iter_units()).segments[0]
    assert flatten_inline_content(ignorable.source) == "whitespace-ish"
    assert flatten_inline_content(ignorable.target or []) == "espace"


def test_a_unit_with_only_an_ignorable_child_is_valid() -> None:
    """"at least one segment OR ignorable" -- an ignorable-only unit
    satisfies the cardinality constraint on its own; a segment is not
    required alongside it."""
    document = loads(
        _document('<ignorable id="i1"><source>x</source></ignorable>')
    )

    report = validate(document)

    assert report.is_valid


def test_an_ignorable_element_round_trips_through_dumps_and_loads() -> None:
    from format_factory.xliff import dumps

    original = loads(
        _document(
            '<ignorable id="i1"><source>keep</source><target>garder</target></ignorable>'
        ),
        mode="preservation",
    )

    reloaded = loads(dumps(original))

    unit = next(reloaded.iter_units())
    assert unit.segments[0].kind == "ignorable"
    assert flatten_inline_content(unit.segments[0].source) == "keep"


def test_a_unit_with_neither_segment_nor_ignorable_is_invalid() -> None:
    """The same cardinality constraint, exercised through the real
    reader/validator pipeline rather than direct Unit/Segment construction:
    a <unit> with no recognized child at all is refused."""
    document = loads(_document(""))

    report = validate(document)

    assert not report.is_valid
    assert "xliff.unit.segment.required" in {item.code for item in report.diagnostics}


def _document_with_file_body(file_body: str) -> bytes:
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<xliff xmlns="{NAMESPACE}" version="2.1" srcLang="en">'
        f'<file id="f1">{file_body}</file>'
        f"</xliff>"
    ).encode()


def test_an_ignorable_only_unit_nested_inside_a_group_still_satisfies_the_cardinality_constraint() -> None:
    """The cardinality constraint applies per-unit regardless of nesting
    depth -- a <group> wrapping an ignorable-only unit is just as valid as
    a top-level one."""
    document = loads(
        _document_with_file_body(
            '<group id="g1"><unit id="u1">'
            '<ignorable id="i1"><source>x</source></ignorable>'
            "</unit></group>"
        )
    )

    report = validate(document)

    assert report.is_valid


def test_one_ignorable_only_unit_among_several_segment_only_units_validates_cleanly() -> None:
    """Each unit is checked independently -- a file mixing ordinary
    segment-only units with an ignorable-only unit is fully valid; the
    ignorable-only unit does not need a sibling segment of its own."""
    document = loads(
        _document_with_file_body(
            '<unit id="u1"><segment id="s1"><source>hi</source></segment></unit>'
            '<unit id="u2"><ignorable id="i1"><source>  </source></ignorable></unit>'
        )
    )

    assert document.unit_count == 2
    report = validate(document)

    assert report.is_valid
