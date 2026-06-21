"""Tests for DIF Sprint 63 gap closure.

Closes:
  GAP-DIF-FOSS-DIF_COLUMN_T-001   (Dif Column Type Variety)
  GAP-DIF-FOSS-DIF_VALUE_VA-001   (Dif Value Variance)
  GAP-DIF-FOSS-DIF_ROW_COL_-001   (Dif Row Col Ratio)
  GAP-DIF-FOSS-DIF_CELL_COU-001   (Dif Cell Count Variance)
  GAP-DIF-FOSS-DIF_STRING_L-001   (Dif String Length Sum)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import (
    dif_column_type_variety,
    dif_value_variance,
    dif_row_col_ratio,
    dif_cell_count_variance,
    dif_string_length_sum,
)

_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = str(_DIR / "minimal-2x2.dif")
_NUMERIC = str(_DIR / "numeric-row.dif")
_SINGLE = str(_DIR / "single-cell.dif")


class TestDifColumnTypeVariety:
    def test_return_type(self):
        assert isinstance(dif_column_type_variety(_MINIMAL), int)

    def test_exact_2_for_minimal(self):
        assert dif_column_type_variety(_MINIMAL) == 2

    def test_exact_1_for_numeric(self):
        assert dif_column_type_variety(_NUMERIC) == 1

    def test_exact_1_for_single(self):
        assert dif_column_type_variety(_SINGLE) == 1

    def test_positive(self):
        assert dif_column_type_variety(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert dif_column_type_variety(_MINIMAL) == dif_column_type_variety(_MINIMAL)


class TestDifValueVariance:
    def test_return_type(self):
        assert isinstance(dif_value_variance(_MINIMAL), (int, float))

    def test_exact_812_25_for_minimal(self):
        assert dif_value_variance(_MINIMAL) == 812.25

    def test_approx_0_667_for_numeric(self):
        assert dif_value_variance(_NUMERIC) == pytest.approx(0.6667, rel=1e-2)

    def test_zero_for_single(self):
        assert dif_value_variance(_SINGLE) == 0.0

    def test_nonnegative(self):
        assert dif_value_variance(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert dif_value_variance(_MINIMAL) == dif_value_variance(_MINIMAL)


class TestDifRowColRatio:
    def test_return_type(self):
        assert isinstance(dif_row_col_ratio(_MINIMAL), (int, float))

    def test_exact_0_125_for_minimal(self):
        assert dif_row_col_ratio(_MINIMAL) == pytest.approx(0.125, rel=1e-3)

    def test_approx_0_333_for_numeric(self):
        assert dif_row_col_ratio(_NUMERIC) == pytest.approx(0.333, rel=1e-2)

    def test_exact_1_0_for_single(self):
        assert dif_row_col_ratio(_SINGLE) == 1.0

    def test_positive(self):
        assert dif_row_col_ratio(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert dif_row_col_ratio(_MINIMAL) == dif_row_col_ratio(_MINIMAL)


class TestDifCellCountVariance:
    def test_return_type(self):
        assert isinstance(dif_cell_count_variance(_MINIMAL), (int, float))

    def test_zero_for_minimal(self):
        assert dif_cell_count_variance(_MINIMAL) == 0.0

    def test_zero_for_numeric(self):
        assert dif_cell_count_variance(_NUMERIC) == 0.0

    def test_zero_for_single(self):
        assert dif_cell_count_variance(_SINGLE) == 0.0

    def test_nonnegative(self):
        assert dif_cell_count_variance(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert dif_cell_count_variance(_MINIMAL) == dif_cell_count_variance(_MINIMAL)


class TestDifStringLengthSum:
    def test_return_type(self):
        assert isinstance(dif_string_length_sum(_MINIMAL), int)

    def test_exact_28_for_minimal(self):
        assert dif_string_length_sum(_MINIMAL) == 28

    def test_zero_for_numeric(self):
        assert dif_string_length_sum(_NUMERIC) == 0

    def test_zero_for_single(self):
        assert dif_string_length_sum(_SINGLE) == 0

    def test_nonnegative(self):
        assert dif_string_length_sum(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert dif_string_length_sum(_MINIMAL) == dif_string_length_sum(_MINIMAL)
