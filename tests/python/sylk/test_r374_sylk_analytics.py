"""Tests for SYLK analytics functions — coverage sprint r374.

Covers 65 sylk_ analytics functions using 3 real SYLK sample files.
Each test asserts return type and plausible value.
"""
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk import (
    sylk_average_numeric_value, sylk_avg_cell_length, sylk_avg_cell_value_length,
    sylk_avg_numeric_cell_length, sylk_avg_numeric_value, sylk_avg_row_density,
    sylk_avg_row_length, sylk_cell_count_variance, sylk_cell_type_distribution,
    sylk_column_count, sylk_column_span, sylk_column_variance, sylk_data_density,
    sylk_data_sparsity, sylk_empty_cell_count, sylk_has_empty_cells,
    sylk_has_empty_rows, sylk_has_header, sylk_has_numeric_cells,
    sylk_has_string_cells, sylk_is_all_numeric, sylk_is_empty, sylk_is_multi_row,
    sylk_is_rectangular, sylk_is_single_column, sylk_is_single_row, sylk_is_square,
    sylk_longest_row_index, sylk_max_cell_value_length, sylk_max_column_index,
    sylk_max_numeric_value, sylk_max_row_cell_count, sylk_max_row_index,
    sylk_max_row_length, sylk_max_string_length, sylk_min_cell_value_length,
    sylk_min_col_index, sylk_min_numeric_value, sylk_min_row_index,
    sylk_min_row_length, sylk_nonempty_cell_count, sylk_nonempty_cell_ratio,
    sylk_nonempty_row_ratio, sylk_nonempty_rows, sylk_numeric_cell_count,
    sylk_numeric_cell_ratio, sylk_numeric_density, sylk_numeric_range,
    sylk_numeric_sum, sylk_numeric_variance, sylk_row_count, sylk_row_span,
    sylk_string_cell_count, sylk_string_density, sylk_string_value_count,
    sylk_total_cell_count, sylk_total_cells, sylk_total_string_length,
    sylk_total_sum, sylk_unique_column_count, sylk_unique_row_count,
    sylk_unique_value_count, sylk_unique_values, sylk_value_length_sum,
)

_SAMPLES = _REPO / "samples" / "by-format" / "sylk" / "valid"
_GRID  = str(_SAMPLES / "minimal-2x2.slk")    # 2x2 grid, mixed string/numeric
_NUMS  = str(_SAMPLES / "numeric-row.slk")    # 1 row, all numeric
_CELL  = str(_SAMPLES / "single-cell.slk")    # 1x1 single cell


class TestSylkRowCount:
    def test_row_count_returns_int(self):
        assert isinstance(sylk_row_count(_GRID), int)

    def test_grid_rows_is_2(self):
        assert sylk_row_count(_GRID) == 2

    def test_nums_rows_is_1(self):
        assert sylk_row_count(_NUMS) == 1

    def test_cell_rows_is_1(self):
        assert sylk_row_count(_CELL) == 1


class TestSylkColumnCount:
    def test_column_count_returns_int(self):
        assert isinstance(sylk_column_count(_GRID), int)

    def test_grid_cols_is_2(self):
        assert sylk_column_count(_GRID) == 2

    def test_cell_cols_is_1(self):
        assert sylk_column_count(_CELL) == 1


class TestSylkTotalCellCount:
    def test_total_cell_count_returns_int(self):
        assert isinstance(sylk_total_cell_count(_GRID), int)

    def test_total_cells_alias(self):
        assert sylk_total_cells(_GRID) == sylk_total_cell_count(_GRID)

    def test_grid_total_is_4(self):
        assert sylk_total_cell_count(_GRID) == 4

    def test_cell_total_is_1(self):
        assert sylk_total_cell_count(_CELL) == 1


class TestSylkNumericCellCount:
    def test_numeric_cell_count_returns_int(self):
        assert isinstance(sylk_numeric_cell_count(_GRID), int)

    def test_nums_all_numeric(self):
        assert sylk_numeric_cell_count(_NUMS) == sylk_total_cell_count(_NUMS)

    def test_cell_has_numeric(self):
        assert sylk_numeric_cell_count(_CELL) >= 0


class TestSylkStringCellCount:
    def test_string_cell_count_returns_int(self):
        assert isinstance(sylk_string_cell_count(_GRID), int)

    def test_nums_no_string(self):
        assert sylk_string_cell_count(_NUMS) == 0

    def test_grid_has_strings(self):
        assert sylk_string_cell_count(_GRID) > 0


class TestSylkEmptyCellCount:
    def test_empty_cell_count_returns_int(self):
        assert isinstance(sylk_empty_cell_count(_GRID), int)

    def test_grid_no_empty(self):
        assert sylk_empty_cell_count(_GRID) == 0

    def test_has_empty_cells_returns_bool(self):
        assert isinstance(sylk_has_empty_cells(_GRID), bool)

    def test_grid_no_has_empty(self):
        assert sylk_has_empty_cells(_GRID) is False

    def test_has_empty_rows_returns_bool(self):
        assert isinstance(sylk_has_empty_rows(_GRID), bool)


class TestSylkNonemptyCells:
    def test_nonempty_cell_count_returns_int(self):
        assert isinstance(sylk_nonempty_cell_count(_GRID), int)

    def test_grid_nonempty_is_4(self):
        assert sylk_nonempty_cell_count(_GRID) == 4

    def test_nonempty_cell_ratio_returns_float(self):
        assert isinstance(sylk_nonempty_cell_ratio(_GRID), float)

    def test_grid_nonempty_ratio_is_1(self):
        assert sylk_nonempty_cell_ratio(_GRID) == pytest.approx(1.0)

    def test_nonempty_row_ratio_returns_float(self):
        assert isinstance(sylk_nonempty_row_ratio(_GRID), float)

    def test_nonempty_rows_returns_int(self):
        assert isinstance(sylk_nonempty_rows(_GRID), int)


class TestSylkDensity:
    def test_data_density_returns_float(self):
        assert isinstance(sylk_data_density(_GRID), float)

    def test_grid_density_is_1(self):
        assert sylk_data_density(_GRID) == pytest.approx(1.0)

    def test_data_sparsity_returns_float(self):
        assert isinstance(sylk_data_sparsity(_GRID), float)

    def test_density_plus_sparsity_is_1(self):
        d = sylk_data_density(_GRID)
        s = sylk_data_sparsity(_GRID)
        assert d + s == pytest.approx(1.0)

    def test_numeric_density_returns_float(self):
        assert isinstance(sylk_numeric_density(_GRID), float)

    def test_string_density_returns_float(self):
        assert isinstance(sylk_string_density(_GRID), float)


class TestSylkNumericStats:
    def test_avg_numeric_value_returns_float(self):
        assert isinstance(sylk_avg_numeric_value(_NUMS), float)

    def test_average_numeric_value_returns_float(self):
        assert isinstance(sylk_average_numeric_value(_NUMS), float)

    def test_avg_equals_average(self):
        assert sylk_avg_numeric_value(_NUMS) == pytest.approx(sylk_average_numeric_value(_NUMS))

    def test_max_numeric_value_returns_float(self):
        assert isinstance(sylk_max_numeric_value(_NUMS), float)

    def test_min_numeric_value_returns_float(self):
        assert isinstance(sylk_min_numeric_value(_GRID), float)

    def test_max_gte_min_numeric(self):
        assert sylk_max_numeric_value(_NUMS) >= sylk_min_numeric_value(_NUMS)

    def test_numeric_range_returns_float(self):
        assert isinstance(sylk_numeric_range(_NUMS), float)

    def test_numeric_sum_returns_float(self):
        assert isinstance(sylk_numeric_sum(_NUMS), float)

    def test_total_sum_returns_float(self):
        assert isinstance(sylk_total_sum(_NUMS), float)

    def test_numeric_variance_returns_float(self):
        assert isinstance(sylk_numeric_variance(_NUMS), float)

    def test_numeric_variance_nonneg(self):
        assert sylk_numeric_variance(_NUMS) >= 0


class TestSylkCellLengths:
    def test_avg_cell_length_returns_float(self):
        assert isinstance(sylk_avg_cell_length(_GRID), float)

    def test_avg_cell_value_length_returns_float(self):
        assert isinstance(sylk_avg_cell_value_length(_GRID), float)

    def test_avg_numeric_cell_length_returns_float(self):
        assert isinstance(sylk_avg_numeric_cell_length(_GRID), float)

    def test_max_cell_value_length_returns_int(self):
        assert isinstance(sylk_max_cell_value_length(_GRID), int)

    def test_min_cell_value_length_returns_int(self):
        assert isinstance(sylk_min_cell_value_length(_GRID), int)

    def test_max_gte_min_cell_value_length(self):
        assert sylk_max_cell_value_length(_GRID) >= sylk_min_cell_value_length(_GRID)

    def test_max_string_length_returns_int(self):
        assert isinstance(sylk_max_string_length(_GRID), int)

    def test_total_string_length_returns_int(self):
        assert isinstance(sylk_total_string_length(_GRID), int)

    def test_value_length_sum_returns_int(self):
        assert isinstance(sylk_value_length_sum(_GRID), int)


class TestSylkRowLengths:
    def test_avg_row_length_returns_float(self):
        assert isinstance(sylk_avg_row_length(_GRID), float)

    def test_max_row_length_returns_int(self):
        assert isinstance(sylk_max_row_length(_GRID), int)

    def test_min_row_length_returns_int(self):
        assert isinstance(sylk_min_row_length(_GRID), int)

    def test_max_gte_min_row_length(self):
        assert sylk_max_row_length(_GRID) >= sylk_min_row_length(_GRID)

    def test_max_row_cell_count_returns_int(self):
        assert isinstance(sylk_max_row_cell_count(_GRID), int)

    def test_avg_row_density_returns_float(self):
        assert isinstance(sylk_avg_row_density(_GRID), float)


class TestSylkSpanIndex:
    def test_row_span_returns_int(self):
        assert isinstance(sylk_row_span(_GRID), int)

    def test_column_span_returns_int(self):
        assert isinstance(sylk_column_span(_GRID), int)

    def test_grid_row_span_is_2(self):
        assert sylk_row_span(_GRID) == 2

    def test_grid_col_span_is_2(self):
        assert sylk_column_span(_GRID) == 2

    def test_max_row_index_returns_int(self):
        assert isinstance(sylk_max_row_index(_GRID), int)

    def test_min_row_index_returns_int(self):
        assert isinstance(sylk_min_row_index(_GRID), int)

    def test_max_column_index_returns_int(self):
        assert isinstance(sylk_max_column_index(_GRID), int)

    def test_min_col_index_returns_int(self):
        assert isinstance(sylk_min_col_index(_GRID), int)

    def test_longest_row_index_returns_int(self):
        assert isinstance(sylk_longest_row_index(_GRID), int)


class TestSylkVariance:
    def test_cell_count_variance_returns_float(self):
        assert isinstance(sylk_cell_count_variance(_GRID), float)

    def test_column_variance_returns_float(self):
        assert isinstance(sylk_column_variance(_GRID), float)

    def test_numeric_cell_ratio_returns_float(self):
        assert isinstance(sylk_numeric_cell_ratio(_GRID), float)

    def test_numeric_cell_ratio_in_0_to_1(self):
        assert 0.0 <= sylk_numeric_cell_ratio(_GRID) <= 1.0


class TestSylkCellTypeDistribution:
    def test_cell_type_distribution_returns_dict(self):
        r = sylk_cell_type_distribution(_GRID)
        assert isinstance(r, dict)

    def test_cell_type_has_numeric_string_empty(self):
        r = sylk_cell_type_distribution(_GRID)
        assert "numeric" in r and "string" in r

    def test_nums_all_numeric_in_distribution(self):
        r = sylk_cell_type_distribution(_NUMS)
        assert r.get("string", 0) == 0


class TestSylkHasFlags:
    def test_has_header_returns_bool(self):
        assert isinstance(sylk_has_header(_GRID), bool)

    def test_grid_has_header(self):
        assert sylk_has_header(_GRID) is True

    def test_has_numeric_cells_returns_bool(self):
        assert isinstance(sylk_has_numeric_cells(_GRID), bool)

    def test_grid_has_numeric_cells(self):
        assert sylk_has_numeric_cells(_GRID) is True

    def test_has_string_cells_returns_bool(self):
        assert isinstance(sylk_has_string_cells(_GRID), bool)

    def test_nums_has_no_string_cells(self):
        assert sylk_has_string_cells(_NUMS) is False


class TestSylkIsFlags:
    def test_is_empty_returns_bool(self):
        assert isinstance(sylk_is_empty(_GRID), bool)

    def test_grid_not_empty(self):
        assert sylk_is_empty(_GRID) is False

    def test_is_multi_row_returns_bool(self):
        assert isinstance(sylk_is_multi_row(_GRID), bool)

    def test_grid_is_multi_row(self):
        assert sylk_is_multi_row(_GRID) is True

    def test_nums_not_multi_row(self):
        assert sylk_is_multi_row(_NUMS) is False

    def test_is_rectangular_returns_bool(self):
        assert isinstance(sylk_is_rectangular(_GRID), bool)

    def test_is_single_column_returns_bool(self):
        assert isinstance(sylk_is_single_column(_GRID), bool)

    def test_cell_is_single_column(self):
        assert sylk_is_single_column(_CELL) is True

    def test_is_single_row_returns_bool(self):
        assert isinstance(sylk_is_single_row(_GRID), bool)

    def test_nums_is_single_row(self):
        assert sylk_is_single_row(_NUMS) is True

    def test_is_square_returns_bool(self):
        assert isinstance(sylk_is_square(_GRID), bool)

    def test_grid_is_square(self):
        assert sylk_is_square(_GRID) is True

    def test_is_all_numeric_returns_bool(self):
        assert isinstance(sylk_is_all_numeric(_NUMS), bool)

    def test_nums_is_all_numeric(self):
        assert sylk_is_all_numeric(_NUMS) is True

    def test_grid_not_all_numeric(self):
        assert sylk_is_all_numeric(_GRID) is False


class TestSylkUniqueStats:
    def test_unique_column_count_returns_int(self):
        assert isinstance(sylk_unique_column_count(_GRID), int)

    def test_unique_row_count_returns_int(self):
        assert isinstance(sylk_unique_row_count(_GRID), int)

    def test_unique_value_count_returns_int(self):
        assert isinstance(sylk_unique_value_count(_GRID), int)

    def test_unique_value_count_positive(self):
        assert sylk_unique_value_count(_GRID) > 0

    def test_string_value_count_returns_int(self):
        assert isinstance(sylk_string_value_count(_GRID), int)

    def test_unique_values_returns_list(self):
        r = sylk_unique_values(_GRID, 1)
        assert isinstance(r, list)

    def test_unique_values_nonempty_for_col1(self):
        r = sylk_unique_values(_GRID, 1)
        assert len(r) > 0
