"""NRRD-PRESERVE-001 -- construct-by-construct preservation reporting.

MUST (SAL-NRRD-OBL-0D0DBFB306769459): "Report every construct that cannot
be preserved before saving, through a loss report API, rather than
failing silently."

Before this slice, preservation_report() collapsed any header/comments/
key-value/array change into a single coarse "nrrd.lossless.document_modified"
issue -- a caller could tell SOMETHING changed but not what. Header fields
and key/value pairs now get one issue per added/removed/changed key.
"""

from __future__ import annotations

from format_factory.nrrd import loads, preservation_report

_SOURCE = (
    b"NRRD0004\r\n"
    b"vendor field: retained\r\n"
    b"type: uint8\r\n"
    b"dimension: 1\r\n"
    b"sizes: 2\r\n"
    b"encoding: raw\r\n"
    b"vendor:=value\r\n\r\n\x01\x02"
)


def _document():
    return loads(_SOURCE, mode="preservation")


def test_an_unmodified_document_reports_no_issues() -> None:
    report = preservation_report(_document())

    assert report.is_lossless is True
    assert report.issues == ()


def test_changing_an_existing_header_field_names_the_field_and_both_values() -> None:
    document = _document()
    document.header["vendor field"] = "changed"

    report = preservation_report(document)

    assert [issue.code for issue in report.issues] == ["nrrd.lossless.header_field_changed"]
    assert report.issues[0].message == (
        "header field 'vendor field' changed from 'retained' to 'changed'"
    )


def test_adding_a_new_header_field_is_reported_as_an_addition() -> None:
    document = _document()
    document.header["a new field"] = "value"

    report = preservation_report(document)

    assert [issue.code for issue in report.issues] == ["nrrd.lossless.header_field_added"]
    assert "a new field" in report.issues[0].message


def test_removing_a_header_field_is_reported_as_a_removal() -> None:
    document = _document()
    del document.header["vendor field"]

    report = preservation_report(document)

    assert [issue.code for issue in report.issues] == ["nrrd.lossless.header_field_removed"]
    assert "vendor field" in report.issues[0].message
    assert "retained" in report.issues[0].message


def test_changing_a_key_value_pair_is_reported_separately_from_header_fields() -> None:
    document = _document()
    document.key_value_pairs["vendor"] = "newvalue"

    report = preservation_report(document)

    assert [issue.code for issue in report.issues] == ["nrrd.lossless.key_value_changed"]
    assert report.issues[0].message == "key/value pair 'vendor' changed from 'value' to 'newvalue'"


def test_multiple_simultaneous_changes_each_produce_their_own_issue() -> None:
    document = _document()
    document.header["vendor field"] = "changed"
    document.key_value_pairs["vendor"] = "newvalue"
    document.key_value_pairs["extra"] = "added"

    report = preservation_report(document)

    codes = sorted(issue.code for issue in report.issues)
    assert codes == [
        "nrrd.lossless.header_field_changed",
        "nrrd.lossless.key_value_added",
        "nrrd.lossless.key_value_changed",
    ]


def test_setting_a_field_to_its_own_value_is_not_reported_as_a_change() -> None:
    document = _document()
    document.header["vendor field"] = "retained"

    report = preservation_report(document)

    assert report.is_lossless is True


def test_changed_comments_are_reported_as_one_coarse_issue() -> None:
    document = _document()
    document.comments = [*document.comments, "# a new comment"]

    report = preservation_report(document)

    assert [issue.code for issue in report.issues] == ["nrrd.lossless.comments_changed"]


def test_changed_array_values_are_reported_as_one_coarse_issue() -> None:
    document = _document()
    document.array = [99, 99]

    report = preservation_report(document)

    assert [issue.code for issue in report.issues] == ["nrrd.lossless.array_changed"]
