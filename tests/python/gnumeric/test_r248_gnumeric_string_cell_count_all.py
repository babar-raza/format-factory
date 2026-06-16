"""Tests for gnumeric_has_any_string_cell and gnumeric_cell_count_all_sheets (Sprint 38)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.gnumeric import gnumeric_has_any_string_cell, gnumeric_cell_count_all_sheets

_DIR = _REPO / "samples" / "by-format" / "gnumeric"
_MINIMAL = str(_DIR / "minimal-spreadsheet.gnumeric")   # 1 string cell "Hello"
_MULTI = str(_DIR / "multi-cell-basic.gnumeric")         # 4 cells: Name, Score, Alice, 42
_EMPTY = str(_DIR / "empty-sheet.gnumeric")              # 0 cells


class TestGnumericHasAnyStringCell:
    def test_return_type(self):
        assert isinstance(gnumeric_has_any_string_cell(_MINIMAL), bool)

    def test_true_for_minimal(self):
        # minimal-spreadsheet.gnumeric has string "Hello"
        assert gnumeric_has_any_string_cell(_MINIMAL) is True

    def test_true_for_multi_cell(self):
        # multi-cell-basic.gnumeric has multiple string cells
        assert gnumeric_has_any_string_cell(_MULTI) is True

    def test_false_for_empty_sheet(self):
        # empty-sheet.gnumeric has no cells
        assert gnumeric_has_any_string_cell(_EMPTY) is False

    def test_consistent_across_calls(self):
        assert gnumeric_has_any_string_cell(_MINIMAL) == gnumeric_has_any_string_cell(_MINIMAL)


class TestGnumericCellCountAllSheets:
    def test_return_type(self):
        assert isinstance(gnumeric_cell_count_all_sheets(_MINIMAL), int)

    def test_exact_1_for_minimal(self):
        # minimal-spreadsheet.gnumeric has exactly 1 cell
        assert gnumeric_cell_count_all_sheets(_MINIMAL) == 1

    def test_exact_4_for_multi(self):
        # multi-cell-basic.gnumeric has exactly 4 cells
        assert gnumeric_cell_count_all_sheets(_MULTI) == 4

    def test_zero_for_empty_sheet(self):
        # empty-sheet.gnumeric has 0 cells
        assert gnumeric_cell_count_all_sheets(_EMPTY) == 0

    def test_nonnegative(self):
        assert gnumeric_cell_count_all_sheets(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert gnumeric_cell_count_all_sheets(_MINIMAL) == gnumeric_cell_count_all_sheets(_MINIMAL)
