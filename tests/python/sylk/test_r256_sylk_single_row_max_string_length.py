"""Tests for sylk_is_single_row and sylk_max_string_length (Sprint 46)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.sylk import sylk_is_single_row, sylk_max_string_length

_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_MINIMAL = str(_DIR / "minimal-2x2.slk")    # 2 rows, 2 cols; strings: Name(4), Value(5), Alpha(5)
_NUMERIC = str(_DIR / "numeric-row.slk")    # 1 row, 3 cols; all numeric: 1, 2, 3
_SINGLE = str(_DIR / "single-cell.slk")     # 1 row, 1 col; numeric: 99


class TestSylkIsSingleRow:
    def test_return_type(self):
        assert isinstance(sylk_is_single_row(_MINIMAL), bool)

    def test_false_for_minimal_2x2(self):
        # minimal-2x2.slk has 2 rows — not a single row
        assert sylk_is_single_row(_MINIMAL) is False

    def test_true_for_numeric_row(self):
        # numeric-row.slk has exactly 1 row
        assert sylk_is_single_row(_NUMERIC) is True

    def test_true_for_single_cell(self):
        # single-cell.slk has exactly 1 row
        assert sylk_is_single_row(_SINGLE) is True

    def test_consistent_across_calls(self):
        assert sylk_is_single_row(_MINIMAL) == sylk_is_single_row(_MINIMAL)

    def test_single_row_implies_row_count_1(self):
        from src.python.sylk import sylk_row_count
        if sylk_is_single_row(_NUMERIC):
            assert sylk_row_count(_NUMERIC) == 1


class TestSylkMaxStringLength:
    def test_return_type(self):
        assert isinstance(sylk_max_string_length(_MINIMAL), int)

    def test_exact_5_for_minimal(self):
        # minimal-2x2.slk: string cells are Name(4), Value(5), Alpha(5) → max=5
        assert sylk_max_string_length(_MINIMAL) == 5

    def test_zero_for_numeric_row(self):
        # numeric-row.slk has no string cells → 0
        assert sylk_max_string_length(_NUMERIC) == 0

    def test_zero_for_single_cell(self):
        # single-cell.slk: cell value 99 is numeric → 0
        assert sylk_max_string_length(_SINGLE) == 0

    def test_nonnegative(self):
        assert sylk_max_string_length(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert sylk_max_string_length(_MINIMAL) == sylk_max_string_length(_MINIMAL)
