"""
test_r55_package_rc.py — R55 Package RC self-contained verification.

Verifies that the R55-rebuilt Python wheels for fods and fodt:
1. Exist as locally-built artifacts (fresh build with R55 source changes)
2. Contain the new writer/parser capabilities (TC-0055/TC-0056 and TC-0057/TC-0060)
3. Round-trip correctly when installed in a clean environment

These tests run against the source tree (not an installed wheel), verifying
the R55 source changes are sound before packaging.

Sprint: FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
publication_authorized: false
commercial_product_ready: false
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_DIR = REPO_ROOT / ".local" / "package-builds" / "python-foss"
sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_build_report() -> list:
    report = BUILD_DIR / "build-report.json"
    if not report.exists():
        return []
    with open(report, encoding="utf-8") as f:
        return json.load(f)


def _entry(module: str) -> dict | None:
    for e in _get_build_report():
        if e.get("module") == module:
            return e
    return None


# ---------------------------------------------------------------------------
# TC-D-001: build report covers fods and fodt (R55 new inclusions)
# ---------------------------------------------------------------------------

class TestR55BuildReportCoversFodsFodt:
    def test_fods_in_build_report(self):
        """fods must appear in R55 build report (added to package matrix in R46)."""
        e = _entry("fods")
        assert e is not None, "fods not found in build-report.json"

    def test_fodt_in_build_report(self):
        """fodt must appear in R55 build report."""
        e = _entry("fodt")
        assert e is not None, "fodt not found in build-report.json"

    def test_fods_status_built(self):
        """fods build must succeed (status='built')."""
        e = _entry("fods")
        assert e is not None
        assert e.get("status") == "built", f"fods status={e.get('status')!r}"

    def test_fodt_status_built(self):
        """fodt build must succeed (status='built')."""
        e = _entry("fodt")
        assert e is not None
        assert e.get("status") == "built", f"fodt status={e.get('status')!r}"

    def test_fods_wheel_artifact_present(self):
        """fods dist/ must contain a .whl file."""
        dist = BUILD_DIR / "aspose-format-factory-fods" / "dist"
        wheels = list(dist.glob("*.whl")) if dist.exists() else []
        assert wheels, f"No .whl in {dist}"

    def test_fodt_wheel_artifact_present(self):
        """fodt dist/ must contain a .whl file."""
        dist = BUILD_DIR / "aspose-format-factory-fodt" / "dist"
        wheels = list(dist.glob("*.whl")) if dist.exists() else []
        assert wheels, f"No .whl in {dist}"

    def test_total_packages_built_is_seven(self):
        """R55 build covers all 7 packages: zst + fodp + fodg + gnumeric + abw + fods + fodt."""
        report = _get_build_report()
        built = [e for e in report if e.get("status") == "built"]
        assert len(built) == 7, f"Expected 7 built, got {len(built)}: {[e.get('module') for e in report]}"


# ---------------------------------------------------------------------------
# TC-D-002: fods source round-trip with R55 features (TC-0055/TC-0056)
# ---------------------------------------------------------------------------

class TestR55FodsSourceRoundTrip:
    """Verify R55 fods source tree (as would be packaged) handles new features."""

    def test_fods_style_metadata_roundtrip(self, tmp_path):
        """TC-0055: auto-styles are preserved on round-trip via source wheel content."""
        from src.python.fods.parser import parse_fods_strict
        from src.python.fods.writer import workbook_to_xml

        fods = tmp_path / "styles.fods"
        fods.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<office:document'
            ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
            ' xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"'
            ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
            ' xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0"'
            ' office:version="1.3"'
            ' office:mimetype="application/vnd.oasis.opendocument.spreadsheet-flat-xml">'
            '<office:automatic-styles'
            ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
            ' xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0">'
            '<style:style style:name="rc55-style" style:family="table-cell"/>'
            '</office:automatic-styles>'
            '<office:body><office:spreadsheet>'
            '<table:table table:name="Sheet1">'
            '<table:table-row><table:table-cell office:value-type="string">'
            '<text:p>data</text:p></table:table-cell></table:table-row>'
            '</table:table></office:spreadsheet></office:body></office:document>',
            encoding="utf-8",
        )
        wb = parse_fods_strict(fods)
        assert "_auto_styles_elem" in wb, "Parser must capture _auto_styles_elem"
        out_xml = workbook_to_xml(wb)
        assert "rc55-style" in out_xml, "Style name must survive round-trip"

    def test_fods_column_defs_roundtrip(self, tmp_path):
        """TC-0056: table-column elements are preserved on round-trip."""
        from src.python.fods.parser import parse_fods_strict
        from src.python.fods.writer import workbook_to_xml

        fods = tmp_path / "coldefs.fods"
        fods.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<office:document'
            ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
            ' xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0"'
            ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
            ' office:version="1.3"'
            ' office:mimetype="application/vnd.oasis.opendocument.spreadsheet-flat-xml">'
            '<office:body><office:spreadsheet>'
            '<table:table table:name="Sheet1">'
            '<table:table-column table:default-cell-style-name="rc55-col"/>'
            '<table:table-row><table:table-cell office:value-type="string">'
            '<text:p>data</text:p></table:table-cell></table:table-row>'
            '</table:table></office:spreadsheet></office:body></office:document>',
            encoding="utf-8",
        )
        wb = parse_fods_strict(fods)
        assert wb["sheets"][0].get("column_defs"), "Parser must capture column_defs"
        out_xml = workbook_to_xml(wb)
        assert "rc55-col" in out_xml, "Column style name must survive round-trip"
        col_pos = out_xml.find("table-column")
        row_pos = out_xml.find("table-row")
        assert col_pos < row_pos, "Column def must precede row data"


# ---------------------------------------------------------------------------
# TC-D-003: fodt source round-trip with R55 features (TC-0057/TC-0060)
# ---------------------------------------------------------------------------

class TestR55FodtSourceRoundTrip:
    """Verify R55 fodt source tree handles inline spans and document ordering."""

    def test_fodt_inline_span_roundtrip(self, tmp_path):
        """TC-0057: inline text:span elements are preserved on round-trip."""
        from src.python.fodt.parser import parse_fodt_strict
        from src.python.fodt.writer import document_to_xml

        fodt = tmp_path / "spans.fodt"
        fodt.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<office:document'
            ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
            ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
            ' office:version="1.3"'
            ' office:mimetype="application/vnd.oasis.opendocument.text-flat-xml">'
            '<office:body><office:text>'
            '<text:p>plain <text:span text:style-name="rc55-bold">bold</text:span> text</text:p>'
            '</office:text></office:body></office:document>',
            encoding="utf-8",
        )
        doc = parse_fodt_strict(fodt)
        block = doc["blocks"][0]
        styled_runs = [r for r in block.get("runs", []) if r.get("style")]
        assert styled_runs, "Parser must capture styled runs"
        assert styled_runs[0]["style"] == "rc55-bold"

        out_xml = document_to_xml(doc)
        assert "rc55-bold" in out_xml, "Style name must survive round-trip"

    def test_fodt_document_ordering_with_content(self, tmp_path):
        """TC-0060: content sequence preserves document order for mixed elements."""
        from src.python.fodt.parser import parse_fodt_strict
        from src.python.fodt.writer import document_to_xml

        fodt = tmp_path / "order.fodt"
        fodt.write_text(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<office:document'
            ' xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"'
            ' xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0"'
            ' office:version="1.3"'
            ' office:mimetype="application/vnd.oasis.opendocument.text-flat-xml">'
            '<office:body><office:text>'
            '<text:p>first</text:p>'
            '<text:p>second</text:p>'
            '</office:text></office:body></office:document>',
            encoding="utf-8",
        )
        doc = parse_fodt_strict(fodt)
        assert "content" in doc, "Neutral model must have content sequence"
        out_xml = document_to_xml(doc)
        first_pos = out_xml.find("first")
        second_pos = out_xml.find("second")
        assert first_pos < second_pos, "Document order must be preserved"
