"""
CSV FOSS gap closure tests.

Closes:
  GAP-CSV-FOSS-CSV_AVG_NUME-001  — csv_avg_numeric_value
  GAP-CSV-FOSS-CSV_EMPTY_CO-001  — csv_empty_column_count
  GAP-CSV-FOSS-CSV_LONGEST_-001  — csv_longest_row_index
  GAP-CSV-FOSS-CSV_TOTAL_ST-001  — csv_total_string_length
  GAP-CSV-FOSS-CSV_IS_SQUAR-001  — csv_is_square
  GAP-CSV-FOSS-CSV_COLUMN_V-001  — csv_column_value_variance (or similar)
  GAP-CSV-FOSS-CSV_HEADER_L-001  — csv_header_length_sum
  GAP-CSV-FOSS-CSV_EMPTY_FI-001  — csv_empty_field_ratio
  GAP-CSV-FOSS-CSV_AVG_FIEL-001  — csv_avg_fields_per_row

Run from repo root:
    python -m pytest tests/python/csv/test_csv_gap_closure_foss.py -v
"""

import sys
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.python.ff_csv.csv_parser import (
    csv_avg_numeric_value,
    csv_empty_column_count,
    csv_longest_row_index,
    csv_total_string_length,
    csv_is_square,
    csv_column_value_variance,
    csv_header_length_sum,
    csv_empty_field_ratio,
    csv_avg_fields_per_row,
)

SAMPLES = REPO_ROOT / "samples" / "by-format" / "csv"
SINGLE = SAMPLES / "single-cell.csv"
TWO_X_TWO = SAMPLES / "minimal-2x2.csv"


class TestCsvAvgNumericValue:
    def test_single_cell_value(self):
        assert csv_avg_numeric_value(SINGLE) == pytest.approx(42.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(csv_avg_numeric_value(SINGLE), (int, float))

    def test_non_negative(self):
        assert csv_avg_numeric_value(SINGLE) >= 0


class TestCsvEmptyColumnCount:
    def test_single_cell_no_empty(self):
        assert csv_empty_column_count(SINGLE) == 0

    def test_two_x_two_no_empty(self):
        assert csv_empty_column_count(TWO_X_TWO) == 0

    def test_returns_int(self):
        assert isinstance(csv_empty_column_count(SINGLE), int)

    def test_non_negative(self):
        for p in [SINGLE, TWO_X_TWO]:
            assert csv_empty_column_count(p) >= 0


class TestCsvLongestRowIndex:
    def test_single_cell_index_zero(self):
        assert csv_longest_row_index(SINGLE) == 0

    def test_returns_int(self):
        assert isinstance(csv_longest_row_index(SINGLE), int)


class TestCsvTotalStringLength:
    def test_single_cell_positive(self):
        assert csv_total_string_length(SINGLE) > 0

    def test_two_x_two_larger(self):
        assert csv_total_string_length(TWO_X_TWO) > csv_total_string_length(SINGLE)

    def test_returns_int(self):
        assert isinstance(csv_total_string_length(SINGLE), int)


class TestCsvIsSquare:
    def test_single_cell_square(self):
        assert csv_is_square(SINGLE) is True

    def test_two_x_two_square(self):
        assert csv_is_square(TWO_X_TWO) is True

    def test_returns_bool(self):
        assert isinstance(csv_is_square(SINGLE), bool)


class TestCsvColumnValueVariance:
    def test_single_cell_zero_variance(self):
        assert csv_column_value_variance(SINGLE) == pytest.approx(0.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(csv_column_value_variance(SINGLE), (int, float))

    def test_non_negative(self):
        for p in [SINGLE, TWO_X_TWO]:
            assert csv_column_value_variance(p) >= 0


class TestCsvHeaderLengthSum:
    def test_single_cell_positive(self):
        assert csv_header_length_sum(SINGLE) > 0

    def test_returns_int(self):
        assert isinstance(csv_header_length_sum(SINGLE), int)

    def test_non_negative(self):
        for p in [SINGLE, TWO_X_TWO]:
            assert csv_header_length_sum(p) >= 0


class TestCsvEmptyFieldRatio:
    def test_single_cell_zero(self):
        assert csv_empty_field_ratio(SINGLE) == pytest.approx(0.0, abs=0.01)

    def test_returns_float(self):
        assert isinstance(csv_empty_field_ratio(SINGLE), (int, float))

    def test_bounded_zero_to_one(self):
        for p in [SINGLE, TWO_X_TWO]:
            r = csv_empty_field_ratio(p)
            assert 0.0 <= r <= 1.0


class TestCsvAvgFieldsPerRow:
    def test_single_cell_one(self):
        assert csv_avg_fields_per_row(SINGLE) == pytest.approx(1.0, abs=0.01)

    def test_two_x_two_two(self):
        assert csv_avg_fields_per_row(TWO_X_TWO) == pytest.approx(2.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(csv_avg_fields_per_row(SINGLE), (int, float))

    def test_positive(self):
        for p in [SINGLE, TWO_X_TWO]:
            assert csv_avg_fields_per_row(p) > 0
