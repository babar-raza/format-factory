"""NRRD-SHAPE-001 -- every per-axis metadata field is arity-validated.

MUST (SAL-NRRD-00010, verified, "Teem NRRD Format Specification -- Sections
1.3 and 6"): "The baseline per-axis metadata fields spacings, axis mins,
axis maxs, centers, labels, and units each carry exactly one value per
declared dimension; kinds and thicknesses are later-version fields."

proof_requirements: positive -- "All per-axis fields across dimensions and
profiles"; negative -- "Every per-axis field with mismatched arity."

Prior to this slice, validator.py checked arity for `sizes` and `kinds`
only. This closes the obligation's declared gap ("not every per-axis
metadata field is arity-validated") by adding typed access
(NrrdDocument.spacings/axis_mins/axis_maxs/centers/labels/units/
thicknesses, mirroring the existing `kinds` property) and a validator check
against every one of them, when present.

labels/units are quote-delimited strings (SAL-NRRD-00009: `\\"` escapes a
literal quote, no other escaping) -- a naive whitespace split would
miscount a label containing an embedded space inside its quotes, so a
dedicated quote-aware tokenizer (_parse_quoted_list) is used for those two
fields specifically; the remaining baseline fields are plain
whitespace-separated numbers or bare words.
"""

from __future__ import annotations

import pytest

from format_factory.nrrd import NrrdDocument, dumps, loads, validate


def _document(**header_overrides: str) -> NrrdDocument:
    """A document whose payload genuinely matches its declared type/sizes
    (round-tripped through dumps/loads), so `validate()` only reports what
    a test actually means to exercise -- per-axis arity -- not an
    incidental payload-length mismatch from a hand-built empty payload."""
    header = {
        "type": "uint16",
        "dimension": "3",
        "sizes": "2 2 2",
        "encoding": "raw",
        "endian": "little",
        **header_overrides,
    }
    element_count = 1
    for token in header["sizes"].split():
        element_count *= int(token)
    draft = NrrdDocument(
        version=5, header=header, payload=b"", array=list(range(element_count))
    )
    return loads(dumps(draft))


# ── Typed per-axis field access ─────────────────────────────────────────────


def test_spacings_parses_as_a_float_list() -> None:
    document = _document(spacings="1.0 2.5 0.5")
    assert document.spacings == [1.0, 2.5, 0.5]


def test_axis_mins_and_axis_maxs_parse_as_float_lists() -> None:
    document = _document(**{"axis mins": "0 0 0", "axis maxs": "10 20 30"})
    assert document.axis_mins == [0.0, 0.0, 0.0]
    assert document.axis_maxs == [10.0, 20.0, 30.0]


def test_centers_parses_as_a_word_list() -> None:
    document = _document(centers="cell node cell")
    assert document.centers == ["cell", "node", "cell"]


def test_thicknesses_parses_as_a_float_list() -> None:
    document = _document(thicknesses="1.0 1.0 2.0")
    assert document.thicknesses == [1.0, 1.0, 2.0]


def test_labels_parses_quote_delimited_strings() -> None:
    document = _document(labels='"x (mm)" "y (mm)" "z (mm)"')
    assert document.labels == ["x (mm)", "y (mm)", "z (mm)"]


def test_units_parses_quote_delimited_strings() -> None:
    document = _document(units='"mm" "mm" "mm"')
    assert document.units == ["mm", "mm", "mm"]


def test_a_label_escapes_an_embedded_quote() -> None:
    """SAL-NRRD-00009: labels escape embedded double quotes with
    backslash-quote. A naive whitespace/quote split would either miscount
    or corrupt this value."""
    document = _document(labels=r'"width \"total\"" "height" "depth"')
    assert document.labels == ['width "total"', "height", "depth"]


def test_a_label_containing_a_space_is_still_one_axis_worth_of_tokens() -> None:
    """The exact failure mode a naive whitespace split would produce: an
    embedded space inside quotes must not be counted as a field separator."""
    document = _document(labels='"time (s)" "position" "depth"')
    assert len(document.labels) == 3


def test_a_labels_own_trailing_whitespace_inside_its_quotes_is_preserved() -> None:
    """Twice investigated and left as a genuinely unsettled spec question
    (whether a quoted field's own trailing whitespace, immediately before
    ITS OWN closing quote, should be exempted from the general
    trailing-whitespace-before-the-line-terminator rule the spec's own
    text permits stripping). Resolved by structural reasoning rather than
    a third re-read of the same spec text: `_parse_header`'s own
    `value.strip()` operates on the WHOLE raw field value, and a
    properly-closed quoted segment's own last character is always its
    closing `"`, never whitespace -- so a plain `.strip()` can only ever
    remove whitespace that comes AFTER the final closing quote (already
    proven permitted), never whitespace inside any quoted segment,
    first, middle, or last, regardless of position. There is therefore
    only one behavior a correct implementation can produce; this proves
    directly, through a full header round trip, that this package
    already produces it -- including the true boundary case (the LAST
    token's own interior trailing space, immediately adjacent to the
    field value's own true end), not only an interior token where the
    answer would be less surprising."""
    document = _document(labels='"leading" "middle " "trailing "')

    assert document.labels == ["leading", "middle ", "trailing "]


def test_absent_fields_are_empty_not_an_error() -> None:
    document = _document()
    assert document.spacings == []
    assert document.labels == []
    assert document.units == []
    assert document.axis_mins == document.axis_maxs == document.centers == []
    assert document.thicknesses == []


def test_per_axis_field_arities_reports_only_fields_actually_present() -> None:
    document = _document(spacings="1 2 3", labels='"a" "b" "c"')
    arities = document.per_axis_field_arities()
    assert arities == {"spacings": 3, "labels": 3}


# ── Positive: every baseline field validates when arity matches, across profiles ──


def test_all_baseline_fields_together_with_correct_arity_validate() -> None:
    document = _document(
        spacings="1.0 1.0 1.0",
        **{"axis mins": "0 0 0", "axis maxs": "1 1 1"},
        centers="cell cell node",
        labels='"x" "y" "z"',
        units='"mm" "mm" "mm"',
    )
    assert validate(document).is_valid


@pytest.mark.parametrize("dimension,sizes", [(1, "4"), (2, "4 4"), (4, "2 2 2 2")])
def test_correct_arity_validates_across_dimensions(dimension: int, sizes: str) -> None:
    spacings = " ".join(["1.0"] * dimension)
    document = _document(dimension=str(dimension), sizes=sizes, spacings=spacings)
    assert validate(document).is_valid


def test_kinds_and_thicknesses_later_version_fields_validate_with_correct_arity() -> None:
    """"kinds and thicknesses are later-version fields" -- both still
    validate for arity like the baseline fields when present; this
    obligation is about arity, not profile-introduction gating (a separate,
    unbuilt capability, NRRD-VERSION-001)."""
    document = _document(kinds="domain domain domain", thicknesses="1.0 1.0 1.0")
    assert validate(document).is_valid


# ── Negative: every per-axis field with mismatched arity is rejected ───────


def test_mismatched_spacings_arity_is_rejected() -> None:
    document = _document(spacings="1.0 2.0")  # 2 values, dimension is 3

    report = validate(document)

    assert not report.is_valid
    assert any(
        item.code == "nrrd.axis_field.arity" and "spacings" in item.message
        for item in report.diagnostics
    )


def test_mismatched_axis_mins_arity_is_rejected() -> None:
    document = _document(**{"axis mins": "0 0"})

    report = validate(document)

    assert not report.is_valid
    assert any("axis mins" in item.message for item in report.diagnostics)


def test_mismatched_axis_maxs_arity_is_rejected() -> None:
    document = _document(**{"axis maxs": "1 1 1 1"})  # 4 values, dimension is 3

    report = validate(document)

    assert not report.is_valid
    assert any("axis maxs" in item.message for item in report.diagnostics)


def test_mismatched_centers_arity_is_rejected() -> None:
    document = _document(centers="cell")

    report = validate(document)

    assert not report.is_valid
    assert any("centers" in item.message for item in report.diagnostics)


def test_mismatched_labels_arity_is_rejected() -> None:
    document = _document(labels='"x" "y"')

    report = validate(document)

    assert not report.is_valid
    assert any("labels" in item.message for item in report.diagnostics)


def test_mismatched_units_arity_is_rejected() -> None:
    document = _document(units='"mm" "mm" "mm" "mm"')

    report = validate(document)

    assert not report.is_valid
    assert any("units" in item.message for item in report.diagnostics)


def test_mismatched_thicknesses_arity_is_rejected() -> None:
    document = _document(thicknesses="1.0")

    report = validate(document)

    assert not report.is_valid
    assert any("thicknesses" in item.message for item in report.diagnostics)


def test_multiple_mismatched_fields_are_all_reported_independently() -> None:
    document = _document(spacings="1.0", centers="cell cell")

    report = validate(document)

    codes = [item.code for item in report.diagnostics if item.code == "nrrd.axis_field.arity"]
    assert len(codes) == 2


def test_an_unterminated_quoted_value_is_rejected() -> None:
    document = _document(labels='"unterminated')

    with pytest.raises(ValueError, match="unterminated"):
        document.labels


def test_a_backslash_not_followed_by_a_quote_is_left_literal() -> None:
    """"support no other escaping" -- an unrecognized backslash sequence is
    not given special meaning (not interpreted as \\n, not rejected as
    illegal); it survives as the literal characters it is."""
    document = _document(units=r'"\n" "mm" "mm"')

    assert document.units[0] == "\\n"


def test_diagnostic_reports_the_declared_and_expected_counts() -> None:
    document = _document(spacings="1.0 2.0")

    report = validate(document)

    (diagnostic,) = [
        item for item in report.diagnostics if item.code == "nrrd.axis_field.arity"
    ]
    assert "2" in diagnostic.message  # declared count
    assert "3" in diagnostic.message  # expected (dimension)
