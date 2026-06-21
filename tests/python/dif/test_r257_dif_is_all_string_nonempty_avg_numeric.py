"""Tests for DIF gap closure (Sprint 40).

Closes:
  GAP-DIF-FOSS-DIF_IS_ALL_S-001   (Dif Is All String)
  GAP-DIF-FOSS-DIF_NONEMPTY-001   (Dif Nonempty Cell Ratio)
  GAP-DIF-FOSS-DIF_AVG_NUME-001   (Dif Avg Numeric Value)
  GAP-DIF-FOSS-DIF_ROW_LENG-001   (Dif Row Length Variance)
  GAP-DIF-FOSS-DIF_EMPTY_CO-001   (Dif Empty Column Count)
  GAP-DIF-FOSS-DIF_LONGEST_-001   (Dif Longest Row Index)
  GAP-DIF-FOSS-DIF_TOTAL_ST-001   (Dif Total String Length)
  GAP-DIF-FOSS-DIF_COLUMN_D-001   (Dif Column Density)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import (
    dif_avg_numeric_value,
    dif_column_density,
    dif_empty_column_count,
    dif_is_all_string,
    dif_longest_row_index,
    dif_nonempty_cell_ratio,
    dif_row_length_variance,
    dif_total_string_length,
)

_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.dif")
_NUMERIC_ROW = str(_DIR / "numeric-row.dif")
_SINGLE_CELL = str(_DIR / "single-cell.dif")


class TestDifIsAllString:
    def test_return_type(self):
        assert isinstance(dif_is_all_string(_MINIMAL_2X2), bool)

    def test_false_for_minimal_2x2(self):
        # has numeric cells -> not all string
        assert dif_is_all_string(_MINIMAL_2X2) is False

    def test_false_for_numeric_row(self):
        assert dif_is_all_string(_NUMERIC_ROW) is False

    def test_false_for_single_cell(self):
        assert dif_is_all_string(_SINGLE_CELL) is False

    def test_consistent_across_calls(self):
        assert dif_is_all_string(_MINIMAL_2X2) == dif_is_all_string(_MINIMAL_2X2)


class TestDifNonemptyCellRatio:
    def test_return_type(self):
        assert isinstance(dif_nonempty_cell_ratio(_MINIMAL_2X2), float)

    def test_exact_1_0_for_minimal_2x2(self):
        assert dif_nonempty_cell_ratio(_MINIMAL_2X2) == 1.0

    def test_exact_1_0_for_numeric_row(self):
        assert dif_nonempty_cell_ratio(_NUMERIC_ROW) == 1.0

    def test_exact_1_0_for_single_cell(self):
        assert dif_nonempty_cell_ratio(_SINGLE_CELL) == 1.0

    def test_between_0_and_1(self):
        ratio = dif_nonempty_cell_ratio(_MINIMAL_2X2)
        assert 0.0 <= ratio <= 1.0

    def test_consistent_across_calls(self):
        assert dif_nonempty_cell_ratio(_MINIMAL_2X2) == dif_nonempty_cell_ratio(_MINIMAL_2X2)


class TestDifAvgNumericValue:
    def test_return_type(self):
        assert isinstance(dif_avg_numeric_value(_MINIMAL_2X2), float)

    def test_exact_70_5_for_minimal_2x2(self):
        assert dif_avg_numeric_value(_MINIMAL_2X2) == 70.5

    def test_exact_2_0_for_numeric_row(self):
        assert dif_avg_numeric_value(_NUMERIC_ROW) == 2.0

    def test_exact_42_0_for_single_cell(self):
        assert dif_avg_numeric_value(_SINGLE_CELL) == 42.0

    def test_nonnegative(self):
        assert dif_avg_numeric_value(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert dif_avg_numeric_value(_MINIMAL_2X2) == dif_avg_numeric_value(_MINIMAL_2X2)


class TestDifRowLengthVariance:
    def test_return_type(self):
        assert isinstance(dif_row_length_variance(_MINIMAL_2X2), float)

    def test_zero_for_minimal_2x2(self):
        # all rows same length -> variance = 0
        assert dif_row_length_variance(_MINIMAL_2X2) == 0.0

    def test_zero_for_numeric_row(self):
        assert dif_row_length_variance(_NUMERIC_ROW) == 0.0

    def test_zero_for_single_cell(self):
        assert dif_row_length_variance(_SINGLE_CELL) == 0.0

    def test_nonnegative(self):
        assert dif_row_length_variance(_MINIMAL_2X2) >= 0.0

    def test_consistent_across_calls(self):
        assert dif_row_length_variance(_MINIMAL_2X2) == dif_row_length_variance(_MINIMAL_2X2)


class TestDifEmptyColumnCount:
    def test_return_type(self):
        assert isinstance(dif_empty_column_count(_MINIMAL_2X2), int)

    def test_zero_for_minimal_2x2(self):
        assert dif_empty_column_count(_MINIMAL_2X2) == 0

    def test_zero_for_numeric_row(self):
        assert dif_empty_column_count(_NUMERIC_ROW) == 0

    def test_zero_for_single_cell(self):
        assert dif_empty_column_count(_SINGLE_CELL) == 0

    def test_nonnegative(self):
        assert dif_empty_column_count(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert dif_empty_column_count(_MINIMAL_2X2) == dif_empty_column_count(_MINIMAL_2X2)


class TestDifLongestRowIndex:
    def test_return_type(self):
        assert isinstance(dif_longest_row_index(_MINIMAL_2X2), int)

    def test_exact_0_for_minimal_2x2(self):
        assert dif_longest_row_index(_MINIMAL_2X2) == 0

    def test_exact_0_for_numeric_row(self):
        assert dif_longest_row_index(_NUMERIC_ROW) == 0

    def test_exact_0_for_single_cell(self):
        assert dif_longest_row_index(_SINGLE_CELL) == 0

    def test_nonnegative(self):
        assert dif_longest_row_index(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert dif_longest_row_index(_MINIMAL_2X2) == dif_longest_row_index(_MINIMAL_2X2)


class TestDifTotalStringLength:
    def test_return_type(self):
        assert isinstance(dif_total_string_length(_MINIMAL_2X2), int)

    def test_exact_36_for_minimal_2x2(self):
        assert dif_total_string_length(_MINIMAL_2X2) == 36

    def test_exact_9_for_numeric_row(self):
        assert dif_total_string_length(_NUMERIC_ROW) == 9

    def test_exact_4_for_single_cell(self):
        assert dif_total_string_length(_SINGLE_CELL) == 4

    def test_nonnegative(self):
        assert dif_total_string_length(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert dif_total_string_length(_MINIMAL_2X2) == dif_total_string_length(_MINIMAL_2X2)


class TestDifColumnDensity:
    def test_return_type(self):
        assert isinstance(dif_column_density(_MINIMAL_2X2), float)

    def test_exact_1_0_for_minimal_2x2(self):
        assert dif_column_density(_MINIMAL_2X2) == 1.0

    def test_exact_1_0_for_numeric_row(self):
        assert dif_column_density(_NUMERIC_ROW) == 1.0

    def test_exact_1_0_for_single_cell(self):
        assert dif_column_density(_SINGLE_CELL) == 1.0

    def test_between_0_and_1(self):
        density = dif_column_density(_MINIMAL_2X2)
        assert 0.0 <= density <= 1.0

    def test_consistent_across_calls(self):
        assert dif_column_density(_MINIMAL_2X2) == dif_column_density(_MINIMAL_2X2)
