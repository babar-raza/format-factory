"""Tests for the ODS Gate 4 prototype parser."""

import sys
from pathlib import Path

# Ensure src/python is on path
_src = Path(__file__).resolve().parents[3] / "src" / "python"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from ods.ods_parser import (
    OdsDocument,
    OdsInvalidContainerError,
    OdsSizeError,
    parse_ods,
    parse_ods_strict,
    probe_ods,
)

SAMPLES = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "ods"


class TestOdsParserBasic:
    """Basic parse tests against valid samples."""

    def test_minimal_spreadsheet(self):
        doc = parse_ods_strict(SAMPLES / "valid" / "minimal-spreadsheet.ods")
        assert isinstance(doc, OdsDocument)
        assert len(doc.sheets) >= 1
        sheet = doc.sheets[0]
        assert sheet.name == "Sheet1"
        assert len(sheet.rows) == 2
        # Row 0: Name, Value (strings)
        assert sheet.rows[0].cells[0].text == "Name"
        assert sheet.rows[0].cells[0].value_type == "string"
        # Row 1: Alpha, 42 (string + float)
        assert sheet.rows[1].cells[0].text == "Alpha"
        assert sheet.rows[1].cells[1].value_type == "float"
        assert sheet.rows[1].cells[1].value == 42.0

    def test_single_cell(self):
        doc = parse_ods_strict(SAMPLES / "valid" / "single-cell.ods")
        assert len(doc.sheets) >= 1
        assert len(doc.sheets[0].rows) >= 1
        assert doc.sheets[0].rows[0].cells[0].text != ""

    def test_numeric_row(self):
        doc = parse_ods_strict(SAMPLES / "valid" / "numeric-row.ods")
        assert len(doc.sheets) >= 1
        row = doc.sheets[0].rows[0]
        float_cells = [c for c in row.cells if c.value_type == "float"]
        assert len(float_cells) >= 3
        values = [c.value for c in float_cells]
        assert values == [1.0, 2.0, 3.0]


class TestOdsParserInvalid:
    """Tests for invalid/malformed ODS files."""

    def test_truncated_zip(self):
        result = parse_ods(SAMPLES / "invalid" / "truncated.ods")
        assert result["ok"] is False
        assert "error" in result

    def test_truncated_raises_strict(self):
        import pytest
        with pytest.raises((OdsInvalidContainerError, Exception)):
            parse_ods_strict(SAMPLES / "invalid" / "truncated.ods")

    def test_nonexistent_file(self):
        result = parse_ods("/nonexistent/fake.ods")
        assert result["ok"] is False


class TestOdsProbe:
    """Tests for probe_ods."""

    def test_probe_valid(self):
        result = probe_ods(SAMPLES / "valid" / "minimal-spreadsheet.ods")
        assert result["valid_container"] is True
        assert result["mimetype"] == "application/vnd.oasis.opendocument.spreadsheet"
        assert "content.xml" in result["entries"]

    def test_probe_nonexistent(self):
        result = probe_ods("/nonexistent/fake.ods")
        assert result["exists"] is False


class TestOdsParserDict:
    """Tests for the dict-returning parse_ods."""

    def test_dict_output(self):
        result = parse_ods(SAMPLES / "valid" / "minimal-spreadsheet.ods")
        assert result["ok"] is True
        assert result["sheet_count"] >= 1
        assert "sheets" in result
        assert result["sheets"][0]["name"] == "Sheet1"
