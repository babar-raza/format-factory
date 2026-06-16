"""Tests for tsv_is_single_column and tsv_is_all_numeric (Sprint 48)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv import tsv_is_single_column, tsv_is_all_numeric

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL = str(_DIR / "minimal-2x2.tsv")    # 2 rows, 2 cols; has string cells
_SINGLE = str(_DIR / "single-cell.tsv")     # 1 row, 1 col; value '42' — numeric
_MULTI = str(_DIR / "multi-column.tsv")     # 2 rows, 4 cols; has string cells


class TestTsvIsSingleColumn:
    def test_return_type(self):
        assert isinstance(tsv_is_single_column(_MINIMAL), bool)

    def test_false_for_minimal_2x2(self):
        # minimal-2x2.tsv has 2 columns
        assert tsv_is_single_column(_MINIMAL) is False

    def test_true_for_single_cell(self):
        # single-cell.tsv has exactly 1 column
        assert tsv_is_single_column(_SINGLE) is True

    def test_false_for_multi_column(self):
        # multi-column.tsv has 4 columns
        assert tsv_is_single_column(_MULTI) is False

    def test_consistent_across_calls(self):
        assert tsv_is_single_column(_SINGLE) == tsv_is_single_column(_SINGLE)

    def test_single_column_implies_col_count_1(self):
        from src.python.tsv import tsv_column_count
        if tsv_is_single_column(_SINGLE):
            assert tsv_column_count(_SINGLE) == 1


class TestTsvIsAllNumeric:
    def test_return_type(self):
        assert isinstance(tsv_is_all_numeric(_MINIMAL), bool)

    def test_false_for_minimal_2x2(self):
        # minimal-2x2.tsv has string cells (names)
        assert tsv_is_all_numeric(_MINIMAL) is False

    def test_true_for_single_cell(self):
        # single-cell.tsv has only '42' — numeric
        assert tsv_is_all_numeric(_SINGLE) is True

    def test_false_for_multi_column(self):
        # multi-column.tsv has string cells
        assert tsv_is_all_numeric(_MULTI) is False

    def test_consistent_across_calls(self):
        assert tsv_is_all_numeric(_SINGLE) == tsv_is_all_numeric(_SINGLE)

    def test_all_numeric_implies_density_1(self):
        from src.python.tsv import tsv_numeric_density
        if tsv_is_all_numeric(_SINGLE):
            assert tsv_numeric_density(_SINGLE) == 1.0
