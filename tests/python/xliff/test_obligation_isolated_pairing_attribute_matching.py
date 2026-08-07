"""XLIFF-PARSE-001 / XLIFF-MODEL-001 / XLIFF-VALIDATE-001 / XLIFF-INLINE-001
/ XLIFF-MODULE-001 / XLIFF-TEXT-001 -- sc/ec canCopy/canDelete/canReorder/
canOverlap attribute-matching, the remaining sub-clause of the isolated-
attribute cluster.

MUST (SAL-XLIFF-OBL-7508113EBF7E4457 and its cross-capability duplicates):
"(XLIFF Core start-code isolation) An sc isolated attribute must be set to
yes if and only if the corresponding ec element is not in the same unit,
and to no otherwise; a source sc with isolated=yes is invalid when a
matching ec referencing its id occurs in the same unit."

This closes the remaining half this cluster's own evidence has honestly
tracked since it was first built (event 220): "The canCopy/canDelete/
canReorder/canOverlap attribute-matching sub-clauses of the same
schematron patterns (F5.1S/F5.1T) remain unbuilt."

Grounded directly in the pinned XLIFF 2.1 schematron's own F5.1S/F5.1T
assertions (inside .local/format-contracts/acquired/xliff/src-xlf-002.bin,
schemas/xliff_core_2.1.sch): when a non-isolated sc has a resolvable
matching ec in the same unit, canCopy/canDelete/canOverlap must be
equivalent between the two -- a "no" value on either side requires "no" on
the other; "yes" and an absent attribute (both meaning the same schema
default of "yes") are mutually compatible with each other. canReorder
follows the same equivalence PLUS one extra rule: sc's own "firstNo" value
requires the matching ec's canReorder to be exactly "no".

Scoped narrowly to exactly this sub-clause: the existing ec-existence
check (_isolated_diagnostics) already proves a matching ec is present
before this function runs at all, so the schematron's clause (a) --
exactly-one-ec, document-order -- is not re-implemented here.
"""

from __future__ import annotations

from format_factory.xliff import InlineElement, Segment, Unit, XliffDocument, XliffFile, validate


def _document(source: list[object]) -> XliffDocument:
    return XliffDocument(
        version="2.1",
        source_language="en",
        target_language=None,
        children=[
            XliffFile(id="f", children=[Unit(id="u", children=[Segment(id="s", source=source)])])
        ],
    )


def test_matching_can_no_values_on_both_sc_and_ec_validate_cleanly() -> None:
    document = _document(
        [
            InlineElement("sc", {"id": "1", "canCopy": "no"}),
            "x",
            InlineElement("ec", {"startRef": "1", "canCopy": "no"}),
        ]
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.isolated.cancopy.mismatch" not in codes


def test_sc_cancopy_no_with_ec_cancopy_absent_is_a_mismatch() -> None:
    document = _document(
        [
            InlineElement("sc", {"id": "1", "canCopy": "no"}),
            "x",
            InlineElement("ec", {"startRef": "1"}),
        ]
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.isolated.cancopy.mismatch" in codes


def test_sc_cancopy_absent_with_ec_cancopy_yes_validates_cleanly_both_are_the_default() -> None:
    document = _document(
        [
            InlineElement("sc", {"id": "1"}),
            "x",
            InlineElement("ec", {"startRef": "1", "canCopy": "yes"}),
        ]
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.isolated.cancopy.mismatch" not in codes


def test_both_cancopy_absent_validates_cleanly() -> None:
    document = _document(
        [InlineElement("sc", {"id": "1"}), "x", InlineElement("ec", {"startRef": "1"})]
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.isolated.cancopy.mismatch" not in codes


def test_candelete_and_canoverlap_mismatches_are_each_independently_reported() -> None:
    document = _document(
        [
            InlineElement("sc", {"id": "1", "canDelete": "no", "canOverlap": "no"}),
            "x",
            InlineElement("ec", {"startRef": "1"}),
        ]
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.isolated.candelete.mismatch" in codes
    assert "xliff.inline.isolated.canoverlap.mismatch" in codes


def test_canreorder_firstno_with_matching_ec_no_validates_cleanly() -> None:
    document = _document(
        [
            InlineElement("sc", {"id": "1", "canReorder": "firstNo"}),
            "x",
            InlineElement("ec", {"startRef": "1", "canReorder": "no"}),
        ]
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.isolated.canreorder.firstno_mismatch" not in codes


def test_canreorder_firstno_with_ec_canreorder_absent_is_a_violation() -> None:
    document = _document(
        [
            InlineElement("sc", {"id": "1", "canReorder": "firstNo"}),
            "x",
            InlineElement("ec", {"startRef": "1"}),
        ]
    )

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.isolated.canreorder.firstno_mismatch" in codes


def test_an_isolated_yes_sc_is_never_checked_for_can_attribute_matching() -> None:
    """This sub-clause only applies to non-isolated sc/ec pairs (the
    schematron context itself excludes isolated='yes'); an isolated sc has
    no matching ec by definition, so there is nothing to compare."""
    document = _document([InlineElement("sc", {"id": "1", "isolated": "yes", "canCopy": "no"})])

    codes = {item.code for item in validate(document).diagnostics}

    assert not any(code.startswith("xliff.inline.isolated.can") for code in codes)


def test_an_sc_with_no_matching_ec_at_all_is_not_checked_for_can_attribute_matching() -> None:
    """Missing-ec is a distinct, separately-reported violation
    (xliff.inline.isolated.missing_ec); with no ec to compare against,
    this sub-clause has nothing to check."""
    document = _document([InlineElement("sc", {"id": "1", "canCopy": "no"})])

    codes = {item.code for item in validate(document).diagnostics}

    assert "xliff.inline.isolated.missing_ec" in codes
    assert "xliff.inline.isolated.cancopy.mismatch" not in codes
