"""Tests for CSV gap closure (Sprint 40).

Closes:
  GAP-CSV-FOSS-CSV_AVG_CELL-001    (Csv Avg Cell Length)
  GAP-CSV-FOSS-CSV_AVG_NUME-001    (Csv Avg Numeric Value)
  GAP-CSV-FOSS-CSV_EMPTY_CO-001    (Csv Empty Column Count)
  GAP-CSV-FOSS-CSV_LONGEST_-001    (Csv Longest Row Index)
  GAP-CSV-FOSS-CSV_TOTAL_ST-001    (Csv Total String Length)
  GAP-CSV-FOSS-CSV_IS_SQUAR-001    (Csv Is Square)
  GAP-CSV-FOSS-CSV_COLUMN_V-001    (Csv Column Value Variance)
  GAP-CSV-FOSS-CSV_HEADER_L-001    (Csv Header Length Sum)
  GAP-CSV-FOSS-CSV_EMPTY_FI-001    (Csv Empty Field Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import (
    csv_avg_cell_length,
    csv_avg_numeric_value,
    csv_column_value_variance,
    csv_empty_column_count,
    csv_empty_field_ratio,
    csv_header_length_sum,
    csv_is_square,
    csv_longest_row_index,
    csv_total_string_length,
)

_DIR = _REPO / "samples" / "by-format" / "csv"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.csv")
_QUOTED = str(_DIR / "quoted-fields.csv")
_SINGLE_CELL = str(_DIR / "single-cell.csv")


class TestCsvAvgCellLength:
    def test_return_type(self):
        assert isinstance(csv_avg_cell_length(_MINIMAL_2X2), float)

    def test_exact_3_0_for_minimal_2x2(self):
        assert csv_avg_cell_length(_MINIMAL_2X2) == 3.0

    def test_exact_2_0_for_single_cell(self):
        assert csv_avg_cell_length(_SINGLE_CELL) == 2.0

    def test_positive(self):
        assert csv_avg_cell_length(_MINIMAL_2X2) > 0

    def test_consistent_across_calls(self):
        assert csv_avg_cell_length(_MINIMAL_2X2) == csv_avg_cell_length(_MINIMAL_2X2)


class TestCsvAvgNumericValue:
    def test_return_type(self):
        assert isinstance(csv_avg_numeric_value(_MINIMAL_2X2), float)

    def test_exact_27_5_for_minimal_2x2(self):
        assert csv_avg_numeric_value(_MINIMAL_2X2) == 27.5

    def test_exact_42_0_for_single_cell(self):
        assert csv_avg_numeric_value(_SINGLE_CELL) == 42.0

    def test_nonnegative(self):
        assert csv_avg_numeric_value(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert csv_avg_numeric_value(_MINIMAL_2X2) == csv_avg_numeric_value(_MINIMAL_2X2)


class TestCsvEmptyColumnCount:
    def test_return_type(self):
        assert isinstance(csv_empty_column_count(_MINIMAL_2X2), int)

    def test_zero_for_minimal_2x2(self):
        assert csv_empty_column_count(_MINIMAL_2X2) == 0

    def test_zero_for_single_cell(self):
        assert csv_empty_column_count(_SINGLE_CELL) == 0

    def test_nonnegative(self):
        assert csv_empty_column_count(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert csv_empty_column_count(_MINIMAL_2X2) == csv_empty_column_count(_MINIMAL_2X2)


class TestCsvLongestRowIndex:
    def test_return_type(self):
        assert isinstance(csv_longest_row_index(_MINIMAL_2X2), int)

    def test_exact_0_for_minimal_2x2(self):
        assert csv_longest_row_index(_MINIMAL_2X2) == 0

    def test_exact_0_for_single_cell(self):
        assert csv_longest_row_index(_SINGLE_CELL) == 0

    def test_nonnegative(self):
        assert csv_longest_row_index(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert csv_longest_row_index(_MINIMAL_2X2) == csv_longest_row_index(_MINIMAL_2X2)


class TestCsvTotalStringLength:
    def test_return_type(self):
        assert isinstance(csv_total_string_length(_MINIMAL_2X2), int)

    def test_exact_12_for_minimal_2x2(self):
        assert csv_total_string_length(_MINIMAL_2X2) == 12

    def test_exact_2_for_single_cell(self):
        assert csv_total_string_length(_SINGLE_CELL) == 2

    def test_nonnegative(self):
        assert csv_total_string_length(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert csv_total_string_length(_MINIMAL_2X2) == csv_total_string_length(_MINIMAL_2X2)


class TestCsvIsSquare:
    def test_return_type(self):
        assert isinstance(csv_is_square(_MINIMAL_2X2), bool)

    def test_true_for_minimal_2x2(self):
        # 2 rows x 2 cols -> square
        assert csv_is_square(_MINIMAL_2X2) is True

    def test_false_for_quoted_fields(self):
        # rows != cols
        assert csv_is_square(_QUOTED) is False

    def test_true_for_single_cell(self):
        # 1x1 -> square
        assert csv_is_square(_SINGLE_CELL) is True

    def test_consistent_across_calls(self):
        assert csv_is_square(_MINIMAL_2X2) == csv_is_square(_MINIMAL_2X2)


class TestCsvColumnValueVariance:
    def test_return_type(self):
        assert isinstance(csv_column_value_variance(_MINIMAL_2X2), float)

    def test_exact_6_25_for_minimal_2x2(self):
        assert csv_column_value_variance(_MINIMAL_2X2) == 6.25

    def test_zero_for_single_cell(self):
        assert csv_column_value_variance(_SINGLE_CELL) == 0.0

    def test_nonnegative(self):
        assert csv_column_value_variance(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert csv_column_value_variance(_MINIMAL_2X2) == csv_column_value_variance(_MINIMAL_2X2)


class TestCsvHeaderLengthSum:
    def test_return_type(self):
        assert isinstance(csv_header_length_sum(_MINIMAL_2X2), int)

    def test_exact_7_for_minimal_2x2(self):
        assert csv_header_length_sum(_MINIMAL_2X2) == 7

    def test_exact_2_for_single_cell(self):
        assert csv_header_length_sum(_SINGLE_CELL) == 2

    def test_nonnegative(self):
        assert csv_header_length_sum(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert csv_header_length_sum(_MINIMAL_2X2) == csv_header_length_sum(_MINIMAL_2X2)


class TestCsvEmptyFieldRatio:
    def test_return_type(self):
        assert isinstance(csv_empty_field_ratio(_MINIMAL_2X2), float)

    def test_zero_for_minimal_2x2(self):
        assert csv_empty_field_ratio(_MINIMAL_2X2) == 0.0

    def test_zero_for_single_cell(self):
        assert csv_empty_field_ratio(_SINGLE_CELL) == 0.0

    def test_between_0_and_1(self):
        ratio = csv_empty_field_ratio(_MINIMAL_2X2)
        assert 0.0 <= ratio <= 1.0

    def test_consistent_across_calls(self):
        assert csv_empty_field_ratio(_MINIMAL_2X2) == csv_empty_field_ratio(_MINIMAL_2X2)
