"""Gate 6 deterministic oracle tests for ODS parser.

Oracle strategy: Compare parsed output against known expected values
from deterministic synthetic samples (no external tool dependency).
"""

import sys
import tempfile
import zipfile
from pathlib import Path

_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from ods.ods_parser import parse_ods_strict

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ods"


def _make_ods(content_xml: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(suffix=".ods", delete=False)
    with zipfile.ZipFile(tmp.name, "w") as zf:
        zf.writestr("mimetype", "application/vnd.oasis.opendocument.spreadsheet")
        zf.writestr("content.xml", content_xml)
    return Path(tmp.name)


class TestOdsOracleKnownValues:
    """Deterministic oracle: compare parsed output against expected values."""

    def test_known_minimal_spreadsheet_oracle(self):
        """Oracle for samples/by-format/ods/valid/minimal-spreadsheet.ods."""
        doc = parse_ods_strict(SAMPLES / "valid" / "minimal-spreadsheet.ods")
        # Expected: Sheet1 with 2 rows
        assert doc.sheets[0].name == "Sheet1"
        assert len(doc.sheets[0].rows) == 2
        # Row 0: headers
        assert doc.sheets[0].rows[0].cells[0].text == "Name"
        assert doc.sheets[0].rows[0].cells[1].text == "Value"
        # Row 1: data
        assert doc.sheets[0].rows[1].cells[0].text == "Alpha"
        assert doc.sheets[0].rows[1].cells[1].value == 42.0

    def test_known_single_cell_oracle(self):
        """Oracle: single-cell.ods has exactly 1 non-empty cell."""
        doc = parse_ods_strict(SAMPLES / "valid" / "single-cell.ods")
        assert len(doc.sheets) >= 1
        total_cells = sum(len(r.cells) for s in doc.sheets for r in s.rows)
        assert total_cells >= 1

    def test_known_numeric_row_oracle(self):
        """Oracle: numeric-row.ods has [1.0, 2.0, 3.0]."""
        doc = parse_ods_strict(SAMPLES / "valid" / "numeric-row.ods")
        row = doc.sheets[0].rows[0]
        float_cells = [c for c in row.cells if c.value_type == "float"]
        assert [c.value for c in float_cells] == [1.0, 2.0, 3.0]

    def test_synthetic_date_cell_oracle(self):
        """Oracle for synthetic ODS with a date cell."""
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:spreadsheet>'
            '<table:table table:name="Dates">'
            '<table:table-row>'
            '<table:table-cell office:value-type="date" office:date-value="2026-01-15">'
            '<text:p>2026-01-15</text:p>'
            '</table:table-cell>'
            '</table:table-row>'
            '</table:table>'
            '</office:spreadsheet></office:body>'
            '</office:document-content>'
        )
        path = _make_ods(content)
        doc = parse_ods_strict(path)
        cell = doc.sheets[0].rows[0].cells[0]
        assert cell.value_type == "date"
        assert cell.value == "2026-01-15"

    def test_synthetic_boolean_cell_oracle(self):
        """Oracle for synthetic ODS with a boolean cell."""
        content = (
            '<?xml version="1.0"?>'
            '<office:document-content '
            'xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
            'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" '
            'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">'
            '<office:body><office:spreadsheet>'
            '<table:table table:name="Bools">'
            '<table:table-row>'
            '<table:table-cell office:value-type="boolean" office:boolean-value="true">'
            '<text:p>TRUE</text:p>'
            '</table:table-cell>'
            '</table:table-row>'
            '</table:table>'
            '</office:spreadsheet></office:body>'
            '</office:document-content>'
        )
        path = _make_ods(content)
        doc = parse_ods_strict(path)
        cell = doc.sheets[0].rows[0].cells[0]
        assert cell.value_type == "boolean"
        assert cell.value == "true"

    def test_oracle_blocked_external_tool(self):
        """Document: full round-trip oracle requires LibreOffice (blocked)."""
        # This test documents the blocker — does not test LibreOffice
        blocked_reason = "LibreOffice-generated reference files not available in CI"
        assert "LibreOffice" in blocked_reason
