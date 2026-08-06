"""XLIFF-INLINE-001 -- paired inline-code integrity: orphan, duplicate, and
illegal-reorder detection.

MUST (SAL-XLIFF-OBL-112C4F88A16C0E1E / SAL-XLIFF-OBL-C788B2558FFB2D9C):
"Prevent or diagnose edits that orphan, duplicate, cross, or illegally
reorder paired codes before save."

Before this slice: duplicate inline `id`s and an `ec` with no matching `sc`
(orphaned) were already diagnosed by validate(). An `ec` whose `startRef`
named an `sc` that appears LATER in the same content sequence -- closing a
code before it opens -- produced zero diagnostics; the check only tested ID
membership in the full element set, not sequence position.
"""

from __future__ import annotations

from format_factory.xliff import (
    InlineElement,
    Segment,
    Unit,
    XliffDocument,
    XliffFile,
    validate,
)


def _document(source: list[object]) -> XliffDocument:
    return XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(
                id="f",
                children=[Unit(id="u", children=[Segment(id="s", source=source)])],
            )
        ],
    )


def test_a_well_formed_paired_code_produces_no_diagnostics() -> None:
    document = _document(
        [InlineElement("sc", {"id": "c1"}), "text", InlineElement("ec", {"startRef": "c1"})]
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.ec.unpaired" not in codes
    assert "xliff.inline.ec.out_of_order" not in codes
    assert "xliff.inline.id.duplicate" not in codes


def test_an_ec_with_no_matching_sc_anywhere_is_orphaned() -> None:
    document = _document([InlineElement("ec", {"id": "e1", "startRef": "missing"})])

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.ec.unpaired" in codes


def test_two_inline_elements_sharing_an_id_are_duplicates() -> None:
    document = _document(
        [
            InlineElement("pc", {"id": "x"}, ["a"]),
            InlineElement("pc", {"id": "x"}, ["b"]),
        ]
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.id.duplicate" in codes


def test_an_ec_referencing_an_sc_that_opens_later_is_out_of_order() -> None:
    document = _document(
        [
            InlineElement("ec", {"id": "e1", "startRef": "c1"}),
            "text",
            InlineElement("sc", {"id": "c1"}),
        ]
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.ec.out_of_order" in codes
    assert "xliff.inline.ec.unpaired" not in codes


def test_two_independently_paired_overlapping_spans_are_not_flagged() -> None:
    """XLIFF's sc/ec model permits overlapping (non-hierarchically-nested)
    annotation spans by design -- this is not the same as an illegal reorder,
    since each ec still closes a code that has already opened by that point."""

    document = _document(
        [
            InlineElement("sc", {"id": "c1"}),
            "one ",
            InlineElement("sc", {"id": "c2"}),
            "two ",
            InlineElement("ec", {"startRef": "c1"}),
            "three ",
            InlineElement("ec", {"startRef": "c2"}),
        ]
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.ec.out_of_order" not in codes
    assert "xliff.inline.ec.unpaired" not in codes
