"""XLIFF-PARSE-001 / XLIFF-MODEL-001 / XLIFF-VALIDATE-001 / XLIFF-INLINE-001 /
XLIFF-MODULE-001 / XLIFF-TEXT-001 -- sc isolated-attribute validation.

MUST (SAL-XLIFF-OBL-7508113EBF7E4457 and its cross-capability duplicates):
"(XLIFF Core start-code isolation) An sc isolated attribute must be set to
yes if and only if the corresponding ec element is not in the same unit,
and to no otherwise; a source sc with isolated=yes is invalid when a
matching ec referencing its id occurs in the same unit."

This is grounded directly in the pinned OASIS XLIFF 2.1 spec's own prose
("The attribute isolated MUST be set to yes if and only if the <ec> element
corresponding to this start marker is not in the same <unit>, and set to no
otherwise" -- 4.2.3.4 sc) and the pinned XLIFF 2.1 schematron's F5S/F5T/
F5.1S patterns (schemas/xliff_core_2.1.sch inside the pinned release ZIP),
which scope the check separately per content type (source vs target) and
across the WHOLE unit, not just one segment -- the spec explicitly permits
a non-isolated sc/ec pair to span multiple segments of one unit ("sc / ec
... pair can reach over segment (but not unit) boundaries"). "no" is the
schema default when the isolated attribute is absent.

Before this slice, no isolated-attribute handling existed anywhere in this
package: the attribute round-tripped generically (InlineElement.attributes
is an untyped dict) but was never read or validated.

Scope note, honestly documented: _isolated_diagnostics() genuinely scans
every segment in the unit, so it detects cross-segment matches correctly
(proven below). The PRE-EXISTING, separate `_validate_inline` per-segment
sc/ec pairing check (`xliff.inline.ec.unpaired`) does NOT look across
segment boundaries within a unit, so a genuinely valid, non-isolated,
cross-segment sc/ec pair would still also trip that older, narrower check
today -- a distinct, pre-existing limitation this slice does not touch or
repair, so this slice's cross-segment fixtures only assert on the new
`xliff.inline.isolated.*` diagnostic codes, not on `report.is_valid`.
"""

from __future__ import annotations

from format_factory.xliff import InlineElement, Segment, Unit, XliffDocument, XliffFile, validate


def _document(source: list[object], *, target: list[object] | None = None) -> XliffDocument:
    return XliffDocument(
        version="2.1",
        source_language="en",
        target_language="fr" if target is not None else None,
        children=[
            XliffFile(
                id="f",
                children=[Unit(id="u", children=[Segment(id="s", source=source, target=target)])],
            )
        ],
    )


def _multi_segment_document(segments: list[Segment]) -> XliffDocument:
    return XliffDocument(
        version="2.1",
        source_language="en",
        target_language="fr",
        children=[XliffFile(id="f", children=[Unit(id="u", children=segments)])],
    )


def test_an_isolated_sc_with_no_matching_ec_anywhere_validates_cleanly() -> None:
    document = _document([InlineElement("sc", {"id": "c1", "isolated": "yes"}), "text"])

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.isolated.unexpected_ec" not in codes
    assert "xliff.inline.isolated.missing_ec" not in codes


def test_an_isolated_sc_with_a_matching_ec_in_the_same_segment_is_a_violation() -> None:
    document = _document(
        [
            InlineElement("sc", {"id": "c1", "isolated": "yes"}),
            "text",
            InlineElement("ec", {"startRef": "c1"}),
        ]
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.isolated.unexpected_ec" in codes


def test_a_non_isolated_sc_with_a_matching_ec_in_the_same_segment_validates_cleanly() -> None:
    document = _document(
        [
            InlineElement("sc", {"id": "c1", "isolated": "no"}),
            "text",
            InlineElement("ec", {"startRef": "c1"}),
        ]
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.isolated.unexpected_ec" not in codes
    assert "xliff.inline.isolated.missing_ec" not in codes


def test_an_sc_with_no_isolated_attribute_defaults_to_no_and_requires_a_matching_ec() -> None:
    document = _document([InlineElement("sc", {"id": "c1"}), "text"])

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.isolated.missing_ec" in codes


def test_an_sc_with_no_isolated_attribute_and_a_matching_ec_validates_cleanly() -> None:
    document = _document(
        [InlineElement("sc", {"id": "c1"}), "text", InlineElement("ec", {"startRef": "c1"})]
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.isolated.missing_ec" not in codes


def test_isolated_yes_with_a_matching_ec_in_a_different_segment_of_the_same_unit_is_still_a_violation() -> None:
    """Proves the check scans the whole unit, not just one segment --
    matching the schematron's ancestor::xlf:unit//xlf:ec[...] scope."""
    document = _multi_segment_document(
        [
            Segment(id="s1", source=[InlineElement("sc", {"id": "c1", "isolated": "yes"})]),
            Segment(id="s2", source=[InlineElement("ec", {"startRef": "c1"})]),
        ]
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.isolated.unexpected_ec" in codes


def test_isolated_check_is_scoped_per_content_type_a_target_side_match_does_not_satisfy_a_source_side_sc() -> None:
    """A source-side sc's isolated attribute is judged only against ec
    elements in source content of the same unit; a matching ec that exists
    only in target content is a different content type and does not count
    -- per the schematron's separate source ([F5S]) and target ([F5T])
    patterns."""
    document = _multi_segment_document(
        [
            Segment(
                id="s1",
                source=[InlineElement("sc", {"id": "c1", "isolated": "yes"})],
                target=None,
            ),
            Segment(id="s2", source=["y"], target=[InlineElement("ec", {"startRef": "c1"})]),
        ]
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.isolated.unexpected_ec" not in codes


def test_a_target_side_isolated_sc_with_a_matching_target_ec_is_a_violation() -> None:
    document = _document(
        ["x"],
        target=[
            InlineElement("sc", {"id": "c1", "isolated": "yes"}),
            InlineElement("ec", {"startRef": "c1"}),
        ],
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.isolated.unexpected_ec" in codes
