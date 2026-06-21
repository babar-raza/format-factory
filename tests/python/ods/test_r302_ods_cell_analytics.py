"""Tests for ods_is_single_cell and ods_min_cell_count_per_sheet (Sprint r302)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_is_single_cell, ods_min_cell_count_per_sheet

_ODS = _REPO / "samples" / "by-format" / "ods" / "valid"


class TestOdsIsSingleCell:
    """Tests for ods_is_single_cell."""

    def test_minimal_spreadsheet_is_not_single(self):
        """minimal-spreadsheet.ods has 4 cells → False."""
        result = ods_is_single_cell(_ODS / "minimal-spreadsheet.ods")
        assert result is False

    def test_numeric_row_is_not_single(self):
        """numeric-row.ods has 3 cells → False."""
        result = ods_is_single_cell(_ODS / "numeric-row.ods")
        assert result is False

    def test_single_cell_is_single(self):
        """single-cell.ods has exactly 1 cell → True."""
        result = ods_is_single_cell(_ODS / "single-cell.ods")
        assert result is True

    def test_returns_bool(self):
        result = ods_is_single_cell(_ODS / "single-cell.ods")
        assert isinstance(result, bool)

    def test_multi_cell_files_return_false(self):
        for f in ["minimal-spreadsheet.ods", "numeric-row.ods"]:
            assert ods_is_single_cell(_ODS / f) is False

    def test_single_true_minimal_false(self):
        r1 = ods_is_single_cell(_ODS / "minimal-spreadsheet.ods")
        r2 = ods_is_single_cell(_ODS / "single-cell.ods")
        assert r1 is False and r2 is True


class TestOdsMinCellCountPerSheet:
    """Tests for ods_min_cell_count_per_sheet."""

    def test_minimal_spreadsheet_min_is_4(self):
        """minimal-spreadsheet.ods has 4 cells in its single sheet."""
        result = ods_min_cell_count_per_sheet(_ODS / "minimal-spreadsheet.ods")
        assert result == 4

    def test_numeric_row_min_is_3(self):
        """numeric-row.ods has 3 cells in its single sheet."""
        result = ods_min_cell_count_per_sheet(_ODS / "numeric-row.ods")
        assert result == 3

    def test_single_cell_min_is_1(self):
        """single-cell.ods has 1 cell in its single sheet."""
        result = ods_min_cell_count_per_sheet(_ODS / "single-cell.ods")
        assert result == 1

    def test_returns_int(self):
        result = ods_min_cell_count_per_sheet(_ODS / "single-cell.ods")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["minimal-spreadsheet.ods", "numeric-row.ods", "single-cell.ods"]:
            assert ods_min_cell_count_per_sheet(_ODS / f) >= 0

    def test_minimal_more_than_single_cell(self):
        r1 = ods_min_cell_count_per_sheet(_ODS / "single-cell.ods")
        r2 = ods_min_cell_count_per_sheet(_ODS / "minimal-spreadsheet.ods")
        assert r2 > r1
