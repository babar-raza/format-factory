"""Tests for ods_rows_to_sheets_ratio and ods_cells_to_rows_ratio (Sprint r306)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_rows_to_sheets_ratio, ods_cells_to_rows_ratio

_ODS = _REPO / "samples" / "by-format" / "ods" / "valid"


class TestOdsRowsToSheetsRatio:
    """Tests for ods_rows_to_sheets_ratio."""

    def test_minimal_spreadsheet_ratio(self):
        """minimal-spreadsheet.ods: 2 rows / 1 sheet = 2.0."""
        assert ods_rows_to_sheets_ratio(_ODS / "minimal-spreadsheet.ods") == 2.0

    def test_numeric_row_ratio(self):
        """numeric-row.ods: 1 row / 1 sheet = 1.0."""
        assert ods_rows_to_sheets_ratio(_ODS / "numeric-row.ods") == 1.0

    def test_single_cell_ratio(self):
        """single-cell.ods: 1 row / 1 sheet = 1.0."""
        assert ods_rows_to_sheets_ratio(_ODS / "single-cell.ods") == 1.0

    def test_returns_float(self):
        assert isinstance(ods_rows_to_sheets_ratio(_ODS / "minimal-spreadsheet.ods"), float)

    def test_minimal_greater_than_single(self):
        r1 = ods_rows_to_sheets_ratio(_ODS / "minimal-spreadsheet.ods")
        r2 = ods_rows_to_sheets_ratio(_ODS / "single-cell.ods")
        assert r1 > r2

    def test_all_nonnegative(self):
        for f in ["minimal-spreadsheet.ods", "numeric-row.ods", "single-cell.ods"]:
            assert ods_rows_to_sheets_ratio(_ODS / f) >= 0.0


class TestOdsCellsToRowsRatio:
    """Tests for ods_cells_to_rows_ratio."""

    def test_minimal_spreadsheet_ratio(self):
        """minimal-spreadsheet.ods: 4 cells / 2 rows = 2.0."""
        assert ods_cells_to_rows_ratio(_ODS / "minimal-spreadsheet.ods") == 2.0

    def test_numeric_row_ratio(self):
        """numeric-row.ods: 3 cells / 1 row = 3.0."""
        assert ods_cells_to_rows_ratio(_ODS / "numeric-row.ods") == 3.0

    def test_single_cell_ratio(self):
        """single-cell.ods: 1 cell / 1 row = 1.0."""
        assert ods_cells_to_rows_ratio(_ODS / "single-cell.ods") == 1.0

    def test_returns_float(self):
        assert isinstance(ods_cells_to_rows_ratio(_ODS / "single-cell.ods"), float)

    def test_all_different(self):
        r1 = ods_cells_to_rows_ratio(_ODS / "minimal-spreadsheet.ods")
        r2 = ods_cells_to_rows_ratio(_ODS / "numeric-row.ods")
        r3 = ods_cells_to_rows_ratio(_ODS / "single-cell.ods")
        assert r1 != r2 and r2 != r3 and r1 != r3

    def test_numeric_row_highest(self):
        r1 = ods_cells_to_rows_ratio(_ODS / "numeric-row.ods")
        r2 = ods_cells_to_rows_ratio(_ODS / "single-cell.ods")
        assert r1 > r2
