"""Tests for ods_total_row_count and ods_sheets_with_data (Sprint r294)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_total_row_count, ods_sheets_with_data

_ODS = _REPO / "samples" / "by-format" / "ods" / "valid"


class TestOdsTotalRowCount:
    """Tests for ods_total_row_count."""

    def test_single_cell_has_one_row(self):
        """single-cell.ods has 1 row."""
        result = ods_total_row_count(_ODS / "single-cell.ods")
        assert result == 1

    def test_minimal_spreadsheet_has_two_rows(self):
        """minimal-spreadsheet.ods has 2 rows."""
        result = ods_total_row_count(_ODS / "minimal-spreadsheet.ods")
        assert result == 2

    def test_numeric_row_has_one_row(self):
        """numeric-row.ods has 1 row."""
        result = ods_total_row_count(_ODS / "numeric-row.ods")
        assert result == 1

    def test_returns_int(self):
        result = ods_total_row_count(_ODS / "minimal-spreadsheet.ods")
        assert isinstance(result, int)

    def test_minimal_spreadsheet_larger_than_single_cell(self):
        r1 = ods_total_row_count(_ODS / "single-cell.ods")
        r2 = ods_total_row_count(_ODS / "minimal-spreadsheet.ods")
        assert r2 > r1

    def test_nonnegative(self):
        for f in ["single-cell.ods", "minimal-spreadsheet.ods", "numeric-row.ods"]:
            result = ods_total_row_count(_ODS / f)
            assert result >= 0


class TestOdsSheetsWithData:
    """Tests for ods_sheets_with_data."""

    def test_single_cell_has_one_sheet_with_data(self):
        """single-cell.ods has 1 sheet with data."""
        result = ods_sheets_with_data(_ODS / "single-cell.ods")
        assert result == 1

    def test_minimal_spreadsheet_has_one_sheet_with_data(self):
        """minimal-spreadsheet.ods has 1 sheet with data."""
        result = ods_sheets_with_data(_ODS / "minimal-spreadsheet.ods")
        assert result == 1

    def test_numeric_row_has_one_sheet_with_data(self):
        """numeric-row.ods has 1 sheet with data."""
        result = ods_sheets_with_data(_ODS / "numeric-row.ods")
        assert result == 1

    def test_returns_int(self):
        result = ods_sheets_with_data(_ODS / "minimal-spreadsheet.ods")
        assert isinstance(result, int)

    def test_sheets_with_data_nonnegative(self):
        for f in ["single-cell.ods", "minimal-spreadsheet.ods", "numeric-row.ods"]:
            result = ods_sheets_with_data(_ODS / f)
            assert result >= 0

    def test_sheets_with_data_greater_than_zero(self):
        """All test files have at least one sheet with data."""
        result = ods_sheets_with_data(_ODS / "single-cell.ods")
        assert result > 0
