"""Tests for TSV gap closure (Sprint 40).

Closes:
  GAP-TSV-FOSS-TSV_NUMERIC_-001   (Tsv Numeric Sum)
  GAP-TSV-FOSS-TSV_AVG_NUME-001   (Tsv Avg Numeric Value)
  GAP-TSV-FOSS-TSV_HAS_DUPL-001   (Tsv Has Duplicates)
  GAP-TSV-FOSS-TSV_EMPTY_CO-001   (Tsv Empty Column Count)
  GAP-TSV-FOSS-TSV_LONGEST_-001   (Tsv Longest Row Index)
  GAP-TSV-FOSS-TSV_MAX_ROW_-001   (Tsv Max Row Cell Count)
  GAP-TSV-FOSS-TSV_DISTINCT-001   (Tsv Distinct Value Ratio)
  GAP-TSV-FOSS-TSV_COLUMN_V-001   (Tsv Column Value Variance)
  GAP-TSV-FOSS-TSV_FIELD_LE-001   (Tsv Field Length Sum)
  GAP-TSV-FOSS-TSV_CELL_TO_-001   (Tsv Cell To Row Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv import (
    tsv_avg_numeric_value,
    tsv_cell_to_row_ratio,
    tsv_column_value_variance,
    tsv_distinct_value_ratio,
    tsv_empty_column_count,
    tsv_field_length_sum,
    tsv_has_duplicates,
    tsv_longest_row_index,
    tsv_max_row_cell_count,
    tsv_numeric_sum,
)

_DIR = _REPO / "samples" / "by-format" / "tsv"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.tsv")
_MULTI_COLUMN = str(_DIR / "multi-column.tsv")
_SINGLE_CELL = str(_DIR / "single-cell.tsv")


class TestTsvNumericSum:
    def test_return_type(self):
        assert isinstance(tsv_numeric_sum(_MINIMAL_2X2), float)

    def test_exact_55_for_minimal_2x2(self):
        assert tsv_numeric_sum(_MINIMAL_2X2) == 55.0

    def test_exact_42_for_single_cell(self):
        assert tsv_numeric_sum(_SINGLE_CELL) == 42.0

    def test_nonnegative(self):
        assert tsv_numeric_sum(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert tsv_numeric_sum(_MINIMAL_2X2) == tsv_numeric_sum(_MINIMAL_2X2)


class TestTsvAvgNumericValue:
    def test_return_type(self):
        assert isinstance(tsv_avg_numeric_value(_MINIMAL_2X2), float)

    def test_exact_27_5_for_minimal_2x2(self):
        assert tsv_avg_numeric_value(_MINIMAL_2X2) == 27.5

    def test_exact_42_for_single_cell(self):
        assert tsv_avg_numeric_value(_SINGLE_CELL) == 42.0

    def test_nonnegative(self):
        assert tsv_avg_numeric_value(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert tsv_avg_numeric_value(_MINIMAL_2X2) == tsv_avg_numeric_value(_MINIMAL_2X2)


class TestTsvHasDuplicates:
    def test_return_type(self):
        assert isinstance(tsv_has_duplicates(_MINIMAL_2X2), bool)

    def test_false_for_minimal_2x2(self):
        assert tsv_has_duplicates(_MINIMAL_2X2) is False

    def test_false_for_multi_column(self):
        assert tsv_has_duplicates(_MULTI_COLUMN) is False

    def test_false_for_single_cell(self):
        assert tsv_has_duplicates(_SINGLE_CELL) is False

    def test_consistent_across_calls(self):
        assert tsv_has_duplicates(_MINIMAL_2X2) == tsv_has_duplicates(_MINIMAL_2X2)


class TestTsvEmptyColumnCount:
    def test_return_type(self):
        assert isinstance(tsv_empty_column_count(_MINIMAL_2X2), int)

    def test_zero_for_minimal_2x2(self):
        assert tsv_empty_column_count(_MINIMAL_2X2) == 0

    def test_zero_for_single_cell(self):
        assert tsv_empty_column_count(_SINGLE_CELL) == 0

    def test_nonnegative(self):
        assert tsv_empty_column_count(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert tsv_empty_column_count(_MINIMAL_2X2) == tsv_empty_column_count(_MINIMAL_2X2)


class TestTsvLongestRowIndex:
    def test_return_type(self):
        assert isinstance(tsv_longest_row_index(_MINIMAL_2X2), int)

    def test_exact_0_for_minimal_2x2(self):
        assert tsv_longest_row_index(_MINIMAL_2X2) == 0

    def test_exact_0_for_multi_column(self):
        assert tsv_longest_row_index(_MULTI_COLUMN) == 0

    def test_exact_0_for_single_cell(self):
        assert tsv_longest_row_index(_SINGLE_CELL) == 0

    def test_nonnegative(self):
        assert tsv_longest_row_index(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert tsv_longest_row_index(_MINIMAL_2X2) == tsv_longest_row_index(_MINIMAL_2X2)


class TestTsvMaxRowCellCount:
    def test_return_type(self):
        assert isinstance(tsv_max_row_cell_count(_MINIMAL_2X2), int)

    def test_exact_2_for_minimal_2x2(self):
        assert tsv_max_row_cell_count(_MINIMAL_2X2) == 2

    def test_exact_4_for_multi_column(self):
        assert tsv_max_row_cell_count(_MULTI_COLUMN) == 4

    def test_exact_1_for_single_cell(self):
        assert tsv_max_row_cell_count(_SINGLE_CELL) == 1

    def test_positive(self):
        assert tsv_max_row_cell_count(_MINIMAL_2X2) >= 1

    def test_consistent_across_calls(self):
        assert tsv_max_row_cell_count(_MINIMAL_2X2) == tsv_max_row_cell_count(_MINIMAL_2X2)


class TestTsvDistinctValueRatio:
    def test_return_type(self):
        assert isinstance(tsv_distinct_value_ratio(_MINIMAL_2X2), float)

    def test_exact_1_0_for_minimal_2x2(self):
        assert tsv_distinct_value_ratio(_MINIMAL_2X2) == 1.0

    def test_exact_1_0_for_single_cell(self):
        assert tsv_distinct_value_ratio(_SINGLE_CELL) == 1.0

    def test_between_0_and_1(self):
        ratio = tsv_distinct_value_ratio(_MINIMAL_2X2)
        assert 0.0 <= ratio <= 1.0

    def test_consistent_across_calls(self):
        assert tsv_distinct_value_ratio(_MINIMAL_2X2) == tsv_distinct_value_ratio(_MINIMAL_2X2)


class TestTsvColumnValueVariance:
    def test_return_type(self):
        assert isinstance(tsv_column_value_variance(_MINIMAL_2X2), float)

    def test_exact_6_25_for_minimal_2x2(self):
        assert tsv_column_value_variance(_MINIMAL_2X2) == 6.25

    def test_zero_for_single_cell(self):
        assert tsv_column_value_variance(_SINGLE_CELL) == 0.0

    def test_nonnegative(self):
        assert tsv_column_value_variance(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert tsv_column_value_variance(_MINIMAL_2X2) == tsv_column_value_variance(_MINIMAL_2X2)


class TestTsvFieldLengthSum:
    def test_return_type(self):
        assert isinstance(tsv_field_length_sum(_MINIMAL_2X2), int)

    def test_exact_12_for_minimal_2x2(self):
        assert tsv_field_length_sum(_MINIMAL_2X2) == 12

    def test_exact_2_for_single_cell(self):
        assert tsv_field_length_sum(_SINGLE_CELL) == 2

    def test_nonnegative(self):
        assert tsv_field_length_sum(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert tsv_field_length_sum(_MINIMAL_2X2) == tsv_field_length_sum(_MINIMAL_2X2)


class TestTsvCellToRowRatio:
    def test_return_type(self):
        assert isinstance(tsv_cell_to_row_ratio(_MINIMAL_2X2), float)

    def test_exact_2_0_for_minimal_2x2(self):
        # 2 cols per row
        assert tsv_cell_to_row_ratio(_MINIMAL_2X2) == 2.0

    def test_exact_4_0_for_multi_column(self):
        assert tsv_cell_to_row_ratio(_MULTI_COLUMN) == 4.0

    def test_exact_1_0_for_single_cell(self):
        assert tsv_cell_to_row_ratio(_SINGLE_CELL) == 1.0

    def test_positive(self):
        assert tsv_cell_to_row_ratio(_MINIMAL_2X2) > 0

    def test_consistent_across_calls(self):
        assert tsv_cell_to_row_ratio(_MINIMAL_2X2) == tsv_cell_to_row_ratio(_MINIMAL_2X2)
