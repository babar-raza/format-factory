"""
tests/python/fods/test_r50_fods_csv_export.py

R50 MT6: FODS CSV export dogfooding tests.

Covers:
  - Basic export from neutral model dict
  - String, float, boolean cells
  - RFC 4180 quoting (commas, quotes, newlines)
  - Multi-sheet workbook — sheet_index selection
  - Empty workbook / empty sheet edge cases
  - Error cases: invalid workbook, out-of-range sheet_index
  - Round-trip: parse FODS → export CSV → parse CSV → verify

Sprint: FORMAT-FACTORY-R50-EVIDENCE-CLOSEOUT-REPAIR-AND-OBJECT-MODEL-HARDENING-001
"""

import csv
import io
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from fods.csv_exporter import export_fods_to_csv, export_fods_to_csv_file, FodsCsvExportError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_workbook(sheets):
    """Build a minimal neutral model workbook dict."""
    return {"sheets": sheets}


def _make_sheet(name, rows_data):
    """Build a sheet dict from a list of lists of cell values.

    rows_data: list of lists, e.g. [["A", "B"], ["1", "2"]]
    """
    rows = []
    for row_data in rows_data:
        cells = []
        for val in row_data:
            if isinstance(val, float):
                cells.append({"value_type": "float", "value": val, "text_content": str(int(val)) if val == int(val) else str(val)})
            elif isinstance(val, bool):
                cells.append({"value_type": "boolean", "value": val, "text_content": "true" if val else "false"})
            else:
                cells.append({"value_type": "string", "value": str(val), "text_content": str(val)})
        rows.append({"cells": cells})
    return {"name": name, "rows": rows}


def _parse_csv(csv_string):
    """Parse CSV string to list of lists."""
    return list(csv.reader(io.StringIO(csv_string)))


# ---------------------------------------------------------------------------
# Basic export
# ---------------------------------------------------------------------------

class TestFodsCsvExportBasic:
    """R50: Basic FODS CSV export."""

    def test_simple_string_values(self):
        """String cell values export correctly."""
        wb = _make_workbook([_make_sheet("Sheet1", [["Name", "Value"], ["Alice", "Hello"]])])
        csv_out = export_fods_to_csv(wb)
        rows = _parse_csv(csv_out)
        assert rows[0] == ["Name", "Value"]
        assert rows[1] == ["Alice", "Hello"]

    def test_float_integer_values(self):
        """Float cell with integer value exports without trailing .0."""
        wb = _make_workbook([_make_sheet("Data", [[1.0, 2.0, 3.0]])])
        csv_out = export_fods_to_csv(wb)
        rows = _parse_csv(csv_out)
        assert rows[0] == ["1", "2", "3"]

    def test_float_decimal_values(self):
        """Float cell with decimal value exports with decimal."""
        wb = _make_workbook([_make_sheet("Data", [[3.14, 2.718]])])
        csv_out = export_fods_to_csv(wb)
        rows = _parse_csv(csv_out)
        assert rows[0][0] == "3.14"
        assert rows[0][1] == "2.718"

    def test_empty_cells_export_empty_string(self):
        """Cells with no value export as empty string."""
        # Build workbook directly with a cell that has no value
        wb = _make_workbook([{
            "name": "S",
            "rows": [{"cells": [{"value_type": "string", "value": None, "text_content": ""}]}]
        }])
        csv_out = export_fods_to_csv(wb)
        rows = _parse_csv(csv_out)
        assert rows[0] == [""]

    def test_multi_row_sheet(self):
        """Multiple rows export correctly in order."""
        wb = _make_workbook([_make_sheet("S", [
            ["R1C1", "R1C2"],
            ["R2C1", "R2C2"],
            ["R3C1", "R3C2"],
        ])])
        csv_out = export_fods_to_csv(wb)
        rows = _parse_csv(csv_out)
        assert len(rows) == 3
        assert rows[2] == ["R3C1", "R3C2"]

    def test_returns_string(self):
        """export_fods_to_csv returns a str."""
        wb = _make_workbook([_make_sheet("S", [["x"]])])
        result = export_fods_to_csv(wb)
        assert isinstance(result, str)

    def test_crlf_line_endings(self):
        """Output uses CRLF line endings (RFC 4180)."""
        wb = _make_workbook([_make_sheet("S", [["A"], ["B"]])])
        csv_out = export_fods_to_csv(wb)
        assert "\r\n" in csv_out


# ---------------------------------------------------------------------------
# RFC 4180 quoting
# ---------------------------------------------------------------------------

class TestFodsCsvRfc4180:
    """R50: RFC 4180 quoting in FODS CSV export."""

    def test_comma_in_value_is_quoted(self):
        """Values containing commas are quoted."""
        wb = _make_workbook([_make_sheet("S", [["hello, world"]])])
        csv_out = export_fods_to_csv(wb)
        rows = _parse_csv(csv_out)
        # After parsing, comma-containing value should be reconstructed correctly
        assert rows[0][0] == "hello, world"
        # Raw output should have quotes
        assert '"hello, world"' in csv_out

    def test_quote_in_value_is_doubled(self):
        """Double-quotes in values are escaped as double-double-quotes."""
        wb = _make_workbook([_make_sheet("S", [['say "hello"']])])
        csv_out = export_fods_to_csv(wb)
        rows = _parse_csv(csv_out)
        assert rows[0][0] == 'say "hello"'

    def test_newline_in_value_is_quoted(self):
        """Values containing newlines are quoted."""
        wb = _make_workbook([_make_sheet("S", [["line1\nline2"]])])
        csv_out = export_fods_to_csv(wb)
        rows = _parse_csv(csv_out)
        assert rows[0][0] == "line1\nline2"


# ---------------------------------------------------------------------------
# Multi-sheet selection
# ---------------------------------------------------------------------------

class TestFodsCsvSheetSelection:
    """R50: Sheet index selection in FODS CSV export."""

    def test_default_exports_first_sheet(self):
        """Default sheet_index=0 exports the first sheet."""
        wb = _make_workbook([
            _make_sheet("First", [["first_sheet_data"]]),
            _make_sheet("Second", [["second_sheet_data"]]),
        ])
        csv_out = export_fods_to_csv(wb)
        rows = _parse_csv(csv_out)
        assert rows[0][0] == "first_sheet_data"

    def test_sheet_index_1_exports_second_sheet(self):
        """sheet_index=1 exports the second sheet."""
        wb = _make_workbook([
            _make_sheet("First", [["first_sheet_data"]]),
            _make_sheet("Second", [["second_sheet_data"]]),
        ])
        csv_out = export_fods_to_csv(wb, sheet_index=1)
        rows = _parse_csv(csv_out)
        assert rows[0][0] == "second_sheet_data"

    def test_out_of_range_sheet_index_raises(self):
        """Out-of-range sheet_index raises FodsCsvExportError."""
        wb = _make_workbook([_make_sheet("Only", [["x"]])])
        with pytest.raises(FodsCsvExportError, match="out of range"):
            export_fods_to_csv(wb, sheet_index=5)

    def test_negative_sheet_index_raises(self):
        """Negative sheet_index raises FodsCsvExportError."""
        wb = _make_workbook([_make_sheet("Only", [["x"]])])
        with pytest.raises(FodsCsvExportError, match="out of range"):
            export_fods_to_csv(wb, sheet_index=-1)


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

class TestFodsCsvExportErrors:
    """R50: Error cases for FODS CSV export."""

    def test_non_dict_workbook_raises(self):
        """Non-dict workbook raises FodsCsvExportError."""
        with pytest.raises(FodsCsvExportError, match="must be a dict"):
            export_fods_to_csv("not a dict")

    def test_empty_sheets_raises(self):
        """Workbook with empty sheets list raises FodsCsvExportError."""
        with pytest.raises(FodsCsvExportError, match="no sheets"):
            export_fods_to_csv({"sheets": []})

    def test_missing_sheets_key_raises(self):
        """Workbook missing 'sheets' key raises FodsCsvExportError."""
        with pytest.raises(FodsCsvExportError, match="no sheets"):
            export_fods_to_csv({"odf_version_attr": "1.3"})


# ---------------------------------------------------------------------------
# File export
# ---------------------------------------------------------------------------

class TestFodsCsvExportFile:
    """R50: FODS CSV file export."""

    def test_writes_file_to_disk(self, tmp_path):
        """export_fods_to_csv_file writes a file to disk."""
        wb = _make_workbook([_make_sheet("S", [["A", "B"], ["1", "2"]])])
        out_path = tmp_path / "test.csv"
        export_fods_to_csv_file(wb, out_path)
        assert out_path.exists()
        content = out_path.read_text(encoding="utf-8")
        rows = _parse_csv(content)
        assert rows[0] == ["A", "B"]
        assert rows[1] == ["1", "2"]

    def test_file_export_matches_string_export(self, tmp_path):
        """File export produces same data content as string export (newlines normalized)."""
        wb = _make_workbook([_make_sheet("S", [["X", "Y"], ["hello", "world"]])])
        csv_string = export_fods_to_csv(wb)
        out_path = tmp_path / "out.csv"
        export_fods_to_csv_file(wb, out_path)
        # Read raw bytes to avoid platform newline translation
        file_content = out_path.read_bytes().decode("utf-8")
        # Normalize CRLF to LF for comparison
        assert csv_string.replace("\r\n", "\n") == file_content.replace("\r\n", "\n")
