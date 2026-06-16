"""Tests for dif_is_single_column and dif_max_string_length (Sprint 47)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import dif_is_single_column, dif_max_string_length

_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = str(_DIR / "minimal-2x2.dif")    # 8 cols: Name,V,Value,V,Alpha,42.0,Beta,99.0
_NUMERIC = str(_DIR / "numeric-row.dif")    # 3 cols: all float 1.0, 2.0, 3.0
_SINGLE = str(_DIR / "single-cell.dif")     # 1 col: float 42.0


class TestDifIsSingleColumn:
    def test_return_type(self):
        assert isinstance(dif_is_single_column(_MINIMAL), bool)

    def test_false_for_minimal(self):
        # minimal-2x2.dif has 8 columns
        assert dif_is_single_column(_MINIMAL) is False

    def test_false_for_numeric_row(self):
        # numeric-row.dif has 3 columns
        assert dif_is_single_column(_NUMERIC) is False

    def test_true_for_single_cell(self):
        # single-cell.dif has exactly 1 column
        assert dif_is_single_column(_SINGLE) is True

    def test_consistent_across_calls(self):
        assert dif_is_single_column(_SINGLE) == dif_is_single_column(_SINGLE)

    def test_single_col_implies_col_count_1(self):
        from src.python.dif import dif_column_count
        if dif_is_single_column(_SINGLE):
            assert dif_column_count(_SINGLE) == 1


class TestDifMaxStringLength:
    def test_return_type(self):
        assert isinstance(dif_max_string_length(_MINIMAL), int)

    def test_exact_7_for_minimal(self):
        # minimal-2x2.dif string cells include '"Value"'(7) and '"Alpha"'(7)
        assert dif_max_string_length(_MINIMAL) == 7

    def test_zero_for_numeric_row(self):
        # numeric-row.dif has only float cells — no string cells
        assert dif_max_string_length(_NUMERIC) == 0

    def test_zero_for_single_cell(self):
        # single-cell.dif has only float 42.0 — no string cells
        assert dif_max_string_length(_SINGLE) == 0

    def test_nonnegative(self):
        assert dif_max_string_length(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert dif_max_string_length(_MINIMAL) == dif_max_string_length(_MINIMAL)
