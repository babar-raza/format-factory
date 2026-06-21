"""Tests for gnumeric_sheets_with_data and gnumeric_total_numeric_count (Sprint r295)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_codec import gnumeric_sheets_with_data, gnumeric_total_numeric_count

_GN = _REPO / "samples" / "by-format" / "gnumeric"


class TestGnumericSheetsWithData:
    """Tests for gnumeric_sheets_with_data."""

    def test_empty_sheet_has_zero(self):
        """empty-sheet.gnumeric has no data in any sheet."""
        result = gnumeric_sheets_with_data(_GN / "empty-sheet.gnumeric")
        assert result == 0

    def test_minimal_spreadsheet_has_one(self):
        """minimal-spreadsheet.gnumeric has 1 sheet with data."""
        result = gnumeric_sheets_with_data(_GN / "minimal-spreadsheet.gnumeric")
        assert result == 1

    def test_multi_cell_basic_has_one(self):
        """multi-cell-basic.gnumeric has 1 sheet with data."""
        result = gnumeric_sheets_with_data(_GN / "multi-cell-basic.gnumeric")
        assert result == 1

    def test_returns_int(self):
        result = gnumeric_sheets_with_data(_GN / "minimal-spreadsheet.gnumeric")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["empty-sheet.gnumeric", "minimal-spreadsheet.gnumeric", "multi-cell-basic.gnumeric"]:
            result = gnumeric_sheets_with_data(_GN / f)
            assert result >= 0

    def test_nonempty_files_have_more_than_empty(self):
        r_empty = gnumeric_sheets_with_data(_GN / "empty-sheet.gnumeric")
        r_minimal = gnumeric_sheets_with_data(_GN / "minimal-spreadsheet.gnumeric")
        assert r_minimal > r_empty


class TestGnumericTotalNumericCount:
    """Tests for gnumeric_total_numeric_count."""

    def test_empty_sheet_has_zero_numerics(self):
        """empty-sheet.gnumeric has no numeric cells."""
        result = gnumeric_total_numeric_count(_GN / "empty-sheet.gnumeric")
        assert result == 0

    def test_minimal_spreadsheet_has_zero_numerics(self):
        """minimal-spreadsheet.gnumeric has no numeric cells (string only)."""
        result = gnumeric_total_numeric_count(_GN / "minimal-spreadsheet.gnumeric")
        assert result == 0

    def test_multi_cell_basic_has_one_numeric(self):
        """multi-cell-basic.gnumeric has 1 numeric cell."""
        result = gnumeric_total_numeric_count(_GN / "multi-cell-basic.gnumeric")
        assert result == 1

    def test_returns_int(self):
        result = gnumeric_total_numeric_count(_GN / "multi-cell-basic.gnumeric")
        assert isinstance(result, int)

    def test_multi_cell_has_more_numerics_than_empty(self):
        r1 = gnumeric_total_numeric_count(_GN / "empty-sheet.gnumeric")
        r2 = gnumeric_total_numeric_count(_GN / "multi-cell-basic.gnumeric")
        assert r2 > r1

    def test_nonnegative(self):
        for f in ["empty-sheet.gnumeric", "minimal-spreadsheet.gnumeric", "multi-cell-basic.gnumeric"]:
            result = gnumeric_total_numeric_count(_GN / f)
            assert result >= 0
