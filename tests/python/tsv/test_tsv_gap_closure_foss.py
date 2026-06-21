"""
TSV FOSS gap closure tests.

Closes:
  GAP-TSV-FOSS-TSV_AVG_NUME-001   — tsv_avg_numeric_value
  GAP-TSV-FOSS-TSV_HAS_DUPL-001   — tsv_has_duplicates
  GAP-TSV-FOSS-TSV_EMPTY_CO-001   — tsv_empty_column_count
  GAP-TSV-FOSS-TSV_LONGEST_-001   — tsv_longest_row_index
  GAP-TSV-FOSS-TSV_MAX_ROW_-001   — tsv_max_row_cell_count
  GAP-TSV-FOSS-TSV_DISTINCT_-001  — tsv_distinct_value_ratio
  GAP-TSV-FOSS-TSV_COLUMN_V-001   — tsv_column_value_variance
  GAP-TSV-FOSS-TSV_FIELD_LE-001   — tsv_field_length_sum
  GAP-TSV-FOSS-TSV_NUMERIC_-001   — tsv_numeric_field_ratio
  GAP-TSV-FOSS-TSV_CELL_TO_-001   — tsv_cell_to_row_ratio
  GAP-TSV-FOSS-TSV_TOTAL_ST-001   — tsv_total_string_length
  GAP-TSV-FOSS-TSV_AVG_FIEL-001   — tsv_avg_fields_per_row

Run from repo root:
    python -m pytest tests/python/tsv/test_tsv_gap_closure_foss.py -v
"""

import sys
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from tsv.tsv_parser import (
    tsv_avg_numeric_value,
    tsv_has_duplicates,
    tsv_empty_column_count,
    tsv_longest_row_index,
    tsv_max_row_cell_count,
    tsv_distinct_value_ratio,
    tsv_column_value_variance,
    tsv_field_length_sum,
    tsv_numeric_field_ratio,
    tsv_cell_to_row_ratio,
    tsv_total_string_length,
    tsv_avg_fields_per_row,
)

SAMPLES = REPO_ROOT / "samples" / "by-format" / "tsv"
SINGLE = SAMPLES / "single-cell.tsv"
TWO_X_TWO = SAMPLES / "minimal-2x2.tsv"
MULTI = SAMPLES / "multi-column.tsv"


class TestTsvAvgNumericValue:
    def test_single_cell_value(self):
        assert tsv_avg_numeric_value(SINGLE) == pytest.approx(42.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(tsv_avg_numeric_value(SINGLE), (int, float))

    def test_non_negative(self):
        for p in [SINGLE, TWO_X_TWO]:
            assert tsv_avg_numeric_value(p) >= 0


class TestTsvHasDuplicates:
    def test_single_cell_no_duplicates(self):
        assert tsv_has_duplicates(SINGLE) is False

    def test_returns_bool(self):
        assert isinstance(tsv_has_duplicates(SINGLE), bool)


class TestTsvEmptyColumnCount:
    def test_single_cell_no_empty(self):
        assert tsv_empty_column_count(SINGLE) == 0

    def test_two_x_two_no_empty(self):
        assert tsv_empty_column_count(TWO_X_TWO) == 0

    def test_returns_int(self):
        assert isinstance(tsv_empty_column_count(SINGLE), int)

    def test_non_negative(self):
        for p in [SINGLE, TWO_X_TWO]:
            assert tsv_empty_column_count(p) >= 0


class TestTsvLongestRowIndex:
    def test_single_cell_index_zero(self):
        assert tsv_longest_row_index(SINGLE) == 0

    def test_returns_int(self):
        assert isinstance(tsv_longest_row_index(SINGLE), int)


class TestTsvMaxRowCellCount:
    def test_single_cell_one(self):
        assert tsv_max_row_cell_count(SINGLE) == 1

    def test_two_x_two_two(self):
        assert tsv_max_row_cell_count(TWO_X_TWO) == 2

    def test_returns_int(self):
        assert isinstance(tsv_max_row_cell_count(SINGLE), int)

    def test_positive(self):
        for p in [SINGLE, TWO_X_TWO]:
            assert tsv_max_row_cell_count(p) > 0


class TestTsvDistinctValueRatio:
    def test_single_cell_one(self):
        assert tsv_distinct_value_ratio(SINGLE) == pytest.approx(1.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(tsv_distinct_value_ratio(SINGLE), (int, float))

    def test_bounded_zero_to_one(self):
        for p in [SINGLE, TWO_X_TWO]:
            r = tsv_distinct_value_ratio(p)
            assert 0.0 <= r <= 1.0


class TestTsvColumnValueVariance:
    def test_single_cell_zero(self):
        assert tsv_column_value_variance(SINGLE) == pytest.approx(0.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(tsv_column_value_variance(SINGLE), (int, float))

    def test_non_negative(self):
        for p in [SINGLE, TWO_X_TWO]:
            assert tsv_column_value_variance(p) >= 0


class TestTsvFieldLengthSum:
    def test_single_cell_positive(self):
        assert tsv_field_length_sum(SINGLE) > 0

    def test_two_x_two_larger(self):
        assert tsv_field_length_sum(TWO_X_TWO) > tsv_field_length_sum(SINGLE)

    def test_returns_int(self):
        assert isinstance(tsv_field_length_sum(SINGLE), int)


class TestTsvNumericFieldRatio:
    def test_single_cell_one(self):
        assert tsv_numeric_field_ratio(SINGLE) == pytest.approx(1.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(tsv_numeric_field_ratio(SINGLE), (int, float))

    def test_bounded_zero_to_one(self):
        for p in [SINGLE, TWO_X_TWO]:
            r = tsv_numeric_field_ratio(p)
            assert 0.0 <= r <= 1.0


class TestTsvCellToRowRatio:
    def test_single_cell_one(self):
        assert tsv_cell_to_row_ratio(SINGLE) == pytest.approx(1.0, abs=0.01)

    def test_two_x_two_two(self):
        assert tsv_cell_to_row_ratio(TWO_X_TWO) == pytest.approx(2.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(tsv_cell_to_row_ratio(SINGLE), (int, float))

    def test_positive(self):
        for p in [SINGLE, TWO_X_TWO]:
            assert tsv_cell_to_row_ratio(p) > 0


class TestTsvTotalStringLength:
    def test_single_cell_positive(self):
        assert tsv_total_string_length(SINGLE) > 0

    def test_two_x_two_larger(self):
        assert tsv_total_string_length(TWO_X_TWO) > tsv_total_string_length(SINGLE)

    def test_returns_int(self):
        assert isinstance(tsv_total_string_length(SINGLE), int)


class TestTsvAvgFieldsPerRow:
    def test_single_cell_one(self):
        assert tsv_avg_fields_per_row(SINGLE) == pytest.approx(1.0, abs=0.01)

    def test_two_x_two_two(self):
        assert tsv_avg_fields_per_row(TWO_X_TWO) == pytest.approx(2.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(tsv_avg_fields_per_row(SINGLE), (int, float))

    def test_positive(self):
        for p in [SINGLE, TWO_X_TWO]:
            assert tsv_avg_fields_per_row(p) > 0
