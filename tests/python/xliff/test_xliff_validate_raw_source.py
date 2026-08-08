"""validate() accepts a raw source directly, not only an already-loaded
XliffDocument, and reports a load-time failure as a non-raising FATAL
diagnostic instead of an uncaught exception -- the same pattern built for
format_factory.nrrd's own validate() (FF6-EVENT-000291), applied here as a
general robustness improvement rather than an obligation closure.
"""

from __future__ import annotations

from pathlib import Path

from format_factory.xliff import load, validate

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "xliff"


def test_malformed_xml_bytes_report_a_fatal_diagnostic_not_a_raise() -> None:
    report = validate(b"not xml at all")

    assert report.is_valid is False
    assert len(report.diagnostics) == 1
    diagnostic = report.diagnostics[0]
    assert diagnostic.code == "xliff.source.unreadable"
    assert diagnostic.severity == "fatal"


def test_a_nonexistent_path_reports_a_fatal_diagnostic_not_a_raise() -> None:
    report = validate(str(SAMPLES / "does-not-exist.xliff"))

    assert report.is_valid is False
    assert report.diagnostics[0].code == "xliff.source.unreadable"


def test_a_valid_source_produces_the_same_report_whether_given_as_a_path_or_a_preloaded_document() -> (
    None
):
    path = SAMPLES / "valid" / "multi-unit.xliff"
    document = load(path)

    from_path = validate(path)
    from_document = validate(document)

    assert from_path.diagnostics == from_document.diagnostics


def test_a_valid_source_given_as_raw_bytes_produces_the_same_report_as_a_path() -> None:
    path = SAMPLES / "valid" / "multi-unit.xliff"

    from_path = validate(path)
    from_bytes = validate(path.read_bytes())

    assert from_path.diagnostics == from_bytes.diagnostics
