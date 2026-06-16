"""Tests for gnumeric_is_empty and gnumeric_max_column_count (Sprint 49)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.gnumeric import gnumeric_is_empty, gnumeric_max_column_count

_DIR = _REPO / "samples" / "by-format" / "gnumeric"
_MINIMAL = str(_DIR / "minimal-spreadsheet.gnumeric")   # 1 cell at (0,0) → 1 col
_MULTI = str(_DIR / "multi-cell-basic.gnumeric")        # 4 cells in 2x2 grid → 2 cols
_EMPTY = str(_DIR / "empty-sheet.gnumeric")             # 0 cells


class TestGnumericIsEmpty:
    def test_return_type(self):
        assert isinstance(gnumeric_is_empty(_MINIMAL), bool)

    def test_false_for_minimal(self):
        # minimal-spreadsheet.gnumeric has 1 cell — not empty
        assert gnumeric_is_empty(_MINIMAL) is False

    def test_false_for_multi_cell(self):
        # multi-cell-basic.gnumeric has 4 cells — not empty
        assert gnumeric_is_empty(_MULTI) is False

    def test_true_for_empty_sheet(self):
        # empty-sheet.gnumeric has 0 cells — is empty
        assert gnumeric_is_empty(_EMPTY) is True

    def test_consistent_across_calls(self):
        assert gnumeric_is_empty(_EMPTY) == gnumeric_is_empty(_EMPTY)

    def test_empty_implies_zero_total_cells(self):
        from src.python.gnumeric import gnumeric_total_cell_count
        if gnumeric_is_empty(_EMPTY):
            assert gnumeric_total_cell_count(_EMPTY) == 0


class TestGnumericMaxColumnCount:
    def test_return_type(self):
        assert isinstance(gnumeric_max_column_count(_MINIMAL), int)

    def test_exact_1_for_minimal(self):
        # minimal-spreadsheet.gnumeric: 1 cell at col 0 → max_col_count=1
        assert gnumeric_max_column_count(_MINIMAL) == 1

    def test_exact_2_for_multi_cell(self):
        # multi-cell-basic.gnumeric: cells at cols 0,1 → max_col_count=2
        assert gnumeric_max_column_count(_MULTI) == 2

    def test_zero_for_empty(self):
        # empty-sheet.gnumeric: no cells → max_col_count=0
        assert gnumeric_max_column_count(_EMPTY) == 0

    def test_nonnegative(self):
        assert gnumeric_max_column_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert gnumeric_max_column_count(_MULTI) == gnumeric_max_column_count(_MULTI)
