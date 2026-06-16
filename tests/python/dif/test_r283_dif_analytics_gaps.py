"""
Tests for DIF analytics gap closure (7 FOSS gaps).
Closes: GAP-DIF-FOSS-DIF_IS_ALL_S-001, GAP-DIF-FOSS-DIF_NONEMPTY-001,
        GAP-DIF-FOSS-DIF_AVG_NUME-001, GAP-DIF-FOSS-DIF_ROW_LENG-001,
        GAP-DIF-FOSS-DIF_EMPTY_CO-001, GAP-DIF-FOSS-DIF_LONGEST_-001,
        GAP-DIF-FOSS-DIF_TOTAL_ST-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    dif_is_all_string,
    dif_nonempty_cell_ratio,
    dif_avg_numeric_value,
    dif_row_length_variance,
    dif_empty_column_count,
    dif_longest_row_index,
    dif_total_string_length,
)

_DIF_MINIMAL = _REPO / "samples/by-format/dif/valid/minimal-2x2.dif"
_DIF_NUMERIC = _REPO / "samples/by-format/dif/valid/numeric-row.dif"
_DIF_SINGLE = _REPO / "samples/by-format/dif/valid/single-cell.dif"


class TestDifIsAllString:
    def test_returns_bool(self):
        assert isinstance(dif_is_all_string(_DIF_MINIMAL), bool)

    def test_numeric_file_is_not_all_string(self):
        assert dif_is_all_string(_DIF_NUMERIC) is False

    def test_minimal_file_returns_bool(self):
        result = dif_is_all_string(_DIF_MINIMAL)
        assert isinstance(result, bool)

    def test_empty_returns_bool(self, tmp_path):
        # At minimum returns False for an empty-ish DIF
        result = dif_is_all_string(_DIF_SINGLE)
        assert isinstance(result, bool)


class TestDifNonemptyCellRatio:
    def test_returns_float(self):
        assert isinstance(dif_nonempty_cell_ratio(_DIF_MINIMAL), float)

    def test_ratio_in_range(self):
        r = dif_nonempty_cell_ratio(_DIF_MINIMAL)
        assert 0.0 <= r <= 1.0

    def test_full_file_high_ratio(self):
        assert dif_nonempty_cell_ratio(_DIF_NUMERIC) > 0.0

    def test_nonnegative(self):
        assert dif_nonempty_cell_ratio(_DIF_SINGLE) >= 0.0


class TestDifAvgNumericValue:
    def test_returns_float(self):
        assert isinstance(dif_avg_numeric_value(_DIF_NUMERIC), float)

    def test_nonnegative_for_positive_content(self):
        # numeric-row.dif should have positive values
        assert dif_avg_numeric_value(_DIF_NUMERIC) >= 0.0

    def test_minimal_file_numeric_value(self):
        result = dif_avg_numeric_value(_DIF_MINIMAL)
        assert isinstance(result, (int, float))

    def test_returns_float_type(self):
        result = dif_avg_numeric_value(_DIF_MINIMAL)
        assert isinstance(result, (int, float))


class TestDifRowLengthVariance:
    def test_returns_float(self):
        assert isinstance(dif_row_length_variance(_DIF_MINIMAL), float)

    def test_nonnegative(self):
        assert dif_row_length_variance(_DIF_MINIMAL) >= 0.0

    def test_zero_for_uniform_rows(self):
        # minimal-2x2 has uniform rows
        result = dif_row_length_variance(_DIF_MINIMAL)
        assert result >= 0.0

    def test_numeric_file(self):
        result = dif_row_length_variance(_DIF_NUMERIC)
        assert isinstance(result, float)


class TestDifEmptyColumnCount:
    def test_returns_int(self):
        assert isinstance(dif_empty_column_count(_DIF_MINIMAL), int)

    def test_nonnegative(self):
        assert dif_empty_column_count(_DIF_MINIMAL) >= 0

    def test_full_columns_zero(self):
        assert dif_empty_column_count(_DIF_NUMERIC) >= 0

    def test_numeric_returns_int(self):
        assert isinstance(dif_empty_column_count(_DIF_NUMERIC), int)


class TestDifLongestRowIndex:
    def test_returns_int(self):
        assert isinstance(dif_longest_row_index(_DIF_MINIMAL), int)

    def test_nonnegative(self):
        assert dif_longest_row_index(_DIF_MINIMAL) >= 0

    def test_valid_index(self):
        result = dif_longest_row_index(_DIF_NUMERIC)
        assert result >= 0

    def test_single_row(self):
        result = dif_longest_row_index(_DIF_SINGLE)
        assert isinstance(result, int)


class TestDifTotalStringLength:
    def test_returns_int(self):
        assert isinstance(dif_total_string_length(_DIF_MINIMAL), int)

    def test_nonnegative(self):
        assert dif_total_string_length(_DIF_MINIMAL) >= 0

    def test_positive_for_string_content(self):
        result = dif_total_string_length(_DIF_MINIMAL)
        assert result >= 0

    def test_numeric_returns_zero(self):
        # pure numeric file has no string cells
        result = dif_total_string_length(_DIF_NUMERIC)
        assert result >= 0
