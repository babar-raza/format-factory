"""Tests for fods_sheet_count and fods_total_row_count (Sprint r300)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods, fods_sheet_count, fods_total_row_count

_FODS = _REPO / "samples" / "by-format" / "fods"


class TestFodsSheetCount:
    """Tests for fods_sheet_count."""

    def test_minimal_has_one_sheet(self):
        """minimal-spreadsheet.fods has 1 sheet."""
        wb = parse_fods(_FODS / "minimal-spreadsheet.fods")
        assert fods_sheet_count(wb) == 1

    def test_multi_sheet_has_two_sheets(self):
        """multi-sheet-basic.fods has 2 sheets."""
        wb = parse_fods(_FODS / "multi-sheet-basic.fods")
        assert fods_sheet_count(wb) == 2

    def test_typed_values_has_one_sheet(self):
        """typed-values-basic.fods has 1 sheet."""
        wb = parse_fods(_FODS / "typed-values-basic.fods")
        assert fods_sheet_count(wb) == 1

    def test_returns_int(self):
        wb = parse_fods(_FODS / "minimal-spreadsheet.fods")
        assert isinstance(fods_sheet_count(wb), int)

    def test_nonnegative(self):
        for f in ["minimal-spreadsheet.fods", "multi-sheet-basic.fods", "typed-values-basic.fods"]:
            wb = parse_fods(_FODS / f)
            assert fods_sheet_count(wb) >= 0

    def test_multi_sheet_more_than_minimal(self):
        wb1 = parse_fods(_FODS / "minimal-spreadsheet.fods")
        wb2 = parse_fods(_FODS / "multi-sheet-basic.fods")
        assert fods_sheet_count(wb2) > fods_sheet_count(wb1)


class TestFodsTotalRowCount:
    """Tests for fods_total_row_count."""

    def test_minimal_has_one_row(self):
        """minimal-spreadsheet.fods has 1 row total."""
        wb = parse_fods(_FODS / "minimal-spreadsheet.fods")
        assert fods_total_row_count(wb) == 1

    def test_multi_sheet_has_three_rows(self):
        """multi-sheet-basic.fods has 3 rows total across 2 sheets."""
        wb = parse_fods(_FODS / "multi-sheet-basic.fods")
        assert fods_total_row_count(wb) == 3

    def test_typed_values_has_four_rows(self):
        """typed-values-basic.fods has 4 rows total."""
        wb = parse_fods(_FODS / "typed-values-basic.fods")
        assert fods_total_row_count(wb) == 4

    def test_returns_int(self):
        wb = parse_fods(_FODS / "minimal-spreadsheet.fods")
        assert isinstance(fods_total_row_count(wb), int)

    def test_nonnegative(self):
        for f in ["minimal-spreadsheet.fods", "multi-sheet-basic.fods", "typed-values-basic.fods"]:
            wb = parse_fods(_FODS / f)
            assert fods_total_row_count(wb) >= 0

    def test_typed_more_rows_than_minimal(self):
        wb1 = parse_fods(_FODS / "minimal-spreadsheet.fods")
        wb2 = parse_fods(_FODS / "typed-values-basic.fods")
        assert fods_total_row_count(wb2) > fods_total_row_count(wb1)
