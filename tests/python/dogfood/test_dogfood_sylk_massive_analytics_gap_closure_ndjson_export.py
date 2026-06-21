"""
tests/python/dogfood/test_dogfood_sylk_massive_analytics_gap_closure_ndjson_export.py

Sprint: dogfood-sylk-analytics-gap-closure-20260617
Dogfood export: SYLK analytics -> NDJSON roundtrip.
Covers 87 previously-untested sylk_* analytics functions on minimal-2x2.slk.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    sylk_average_numeric_value,
    sylk_avg_cell_length,
    sylk_avg_cell_length_per_row,
    sylk_avg_cell_value_length,
    sylk_avg_cols_per_row,
    sylk_avg_numeric_cell_length,
    sylk_avg_numeric_sum_per_row,
    sylk_avg_row_density,
    sylk_avg_row_length,
    sylk_avg_value_length,
    sylk_cell_count_per_row_avg,
    sylk_cell_count_variance,
    sylk_cell_row_count_variance,
    sylk_cell_sparsity,
    sylk_cell_type_distribution,
    sylk_cells_to_rows_ratio,
    sylk_column_fill_rate,
    sylk_column_span,
    sylk_column_variance,
    sylk_data_density,
    sylk_distinct_column_count,
    sylk_distinct_string_count,
    sylk_empty_cell_count,
    sylk_first_row_cell_count,
    sylk_has_empty_cells,
    sylk_has_empty_rows,
    sylk_has_header,
    sylk_has_multi_col_rows,
    sylk_has_numeric_cells,
    sylk_has_only_numeric,
    sylk_has_string_cells,
    sylk_has_string_cols,
    sylk_is_all_numeric,
    sylk_is_empty,
    sylk_is_multi_row,
    sylk_is_rectangular,
    sylk_is_single_column,
    sylk_is_single_row,
    sylk_is_square,
    sylk_is_wider_than_tall,
    sylk_longest_row_index,
    sylk_max_cell_text_length,
    sylk_max_cells_in_col,
    sylk_max_column_index,
    sylk_max_row_cell_count,
    sylk_max_row_index,
    sylk_max_row_length,
    sylk_max_row_sum,
    sylk_max_string_length,
    sylk_max_value_count,
    sylk_min_cell_text_length,
    sylk_min_col_index,
    sylk_min_column_sum,
    sylk_min_row_cell_count,
    sylk_min_row_index,
    sylk_min_row_length,
    sylk_nonempty_cell_count,
    sylk_nonempty_cell_ratio,
    sylk_nonempty_col_count,
    sylk_nonempty_row_ratio,
    sylk_nonempty_rows,
    sylk_numeric_cell_count,
    sylk_numeric_cell_ratio,
    sylk_numeric_cell_sum,
    sylk_numeric_column_count,
    sylk_numeric_range,
    sylk_numeric_sum,
    sylk_numeric_to_string_ratio,
    sylk_numeric_variance,
    sylk_row_col_ratio,
    sylk_row_density,
    sylk_row_density_avg,
    sylk_row_density_variance,
    sylk_row_fill_rate,
    sylk_row_span,
    sylk_string_cell_count,
    sylk_string_cells_exceed_numeric,
    sylk_string_column_count,
    sylk_string_density,
    sylk_string_length_sum,
    sylk_string_value_count,
    sylk_text_cell_ratio,
    sylk_total_cells,
    sylk_total_string_length,
    sylk_total_sum,
    sylk_unique_cell_value_count,
    sylk_unique_column_count,
    sylk_unique_row_count,
    sylk_unique_value_count,
    sylk_unique_values,
    sylk_value_sum,
    sylk_value_type_variety,
    sylk_value_variance,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_SYLK_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_S = str(_SYLK_DIR / "minimal-2x2.slk")


class TestSylkMassiveAnalyticsGapClosureNdjsonExport:
    """87 SYLK analytics functions -> NDJSON dogfood export on minimal-2x2.slk."""

    # --- numeric analytics ---

    def test_average_numeric_value(self):
        assert sylk_average_numeric_value(_S) == 42.0

    def test_avg_cell_length(self):
        assert sylk_avg_cell_length(_S) == 4.0

    def test_avg_cell_length_per_row(self):
        assert sylk_avg_cell_length_per_row(_S) == 4.0

    def test_avg_cell_value_length(self):
        assert sylk_avg_cell_value_length(_S) == 4.0

    def test_avg_cols_per_row(self):
        assert sylk_avg_cols_per_row(_S) == 2.0

    def test_avg_numeric_cell_length(self):
        assert sylk_avg_numeric_cell_length(_S) == 2.0

    def test_avg_numeric_sum_per_row(self):
        assert sylk_avg_numeric_sum_per_row(_S) == 21.0

    def test_avg_row_density(self):
        assert sylk_avg_row_density(_S) == 2.0

    def test_avg_row_length(self):
        assert sylk_avg_row_length(_S) == 2.0

    def test_avg_value_length(self):
        assert sylk_avg_value_length(_S) == 4.0

    def test_cell_count_per_row_avg(self):
        assert sylk_cell_count_per_row_avg(_S) == 2.0

    def test_cell_count_variance(self):
        assert sylk_cell_count_variance(_S) == 0.0

    def test_cell_row_count_variance(self):
        assert sylk_cell_row_count_variance(_S) == 0.0

    def test_cell_sparsity(self):
        assert sylk_cell_sparsity(_S) == 0.0

    def test_cell_type_distribution(self):
        d = sylk_cell_type_distribution(_S)
        assert d["numeric"] == 1
        assert d["string"] == 3
        assert d["empty"] == 0

    def test_cells_to_rows_ratio(self):
        assert sylk_cells_to_rows_ratio(_S) == 2.0

    def test_column_fill_rate(self):
        val = sylk_column_fill_rate(_S)
        assert abs(val - 0.4444) < 0.001

    def test_column_span(self):
        assert sylk_column_span(_S) == 2

    def test_column_variance(self):
        assert sylk_column_variance(_S) == 0.0

    def test_data_density(self):
        assert sylk_data_density(_S) == 1.0

    def test_distinct_column_count(self):
        assert sylk_distinct_column_count(_S) == 2

    def test_distinct_string_count(self):
        assert sylk_distinct_string_count(_S) == 3

    def test_empty_cell_count(self):
        assert sylk_empty_cell_count(_S) == 0

    def test_first_row_cell_count(self):
        assert sylk_first_row_cell_count(_S) == 2

    def test_longest_row_index(self):
        assert sylk_longest_row_index(_S) == 1

    def test_max_cell_text_length(self):
        assert sylk_max_cell_text_length(_S) == 5

    def test_max_cells_in_col(self):
        assert sylk_max_cells_in_col(_S) == 2

    def test_max_column_index(self):
        assert sylk_max_column_index(_S) == 2

    def test_max_row_cell_count(self):
        assert sylk_max_row_cell_count(_S) == 2

    def test_max_row_index(self):
        assert sylk_max_row_index(_S) == 2

    def test_max_row_length(self):
        assert sylk_max_row_length(_S) == 2

    def test_max_row_sum(self):
        assert sylk_max_row_sum(_S) == 42.0

    def test_max_string_length(self):
        assert sylk_max_string_length(_S) == 5

    def test_max_value_count(self):
        assert sylk_max_value_count(_S) == 1

    def test_min_cell_text_length(self):
        assert sylk_min_cell_text_length(_S) == 2

    def test_min_col_index(self):
        assert sylk_min_col_index(_S) == 1

    def test_min_column_sum(self):
        assert sylk_min_column_sum(_S) == 42.0

    def test_min_row_cell_count(self):
        assert sylk_min_row_cell_count(_S) == 2

    def test_min_row_index(self):
        assert sylk_min_row_index(_S) == 1

    def test_min_row_length(self):
        assert sylk_min_row_length(_S) == 2

    def test_nonempty_cell_count(self):
        assert sylk_nonempty_cell_count(_S) == 4

    def test_nonempty_cell_ratio(self):
        assert sylk_nonempty_cell_ratio(_S) == 1.0

    def test_nonempty_col_count(self):
        assert sylk_nonempty_col_count(_S) == 2

    def test_nonempty_row_ratio(self):
        assert sylk_nonempty_row_ratio(_S) == 1.0

    def test_nonempty_rows(self):
        assert sylk_nonempty_rows(_S) == 2

    def test_numeric_cell_count(self):
        assert sylk_numeric_cell_count(_S) == 1

    def test_numeric_cell_ratio(self):
        assert sylk_numeric_cell_ratio(_S) == 0.25

    def test_numeric_cell_sum(self):
        assert sylk_numeric_cell_sum(_S) == 42.0

    def test_numeric_column_count(self):
        assert sylk_numeric_column_count(_S) == 1

    def test_numeric_range(self):
        assert sylk_numeric_range(_S) == 0.0

    def test_numeric_sum(self):
        assert sylk_numeric_sum(_S) == 42.0

    def test_numeric_to_string_ratio(self):
        val = sylk_numeric_to_string_ratio(_S)
        assert abs(val - 0.3333) < 0.001

    def test_numeric_variance(self):
        assert sylk_numeric_variance(_S) == 0.0

    def test_row_col_ratio(self):
        assert sylk_row_col_ratio(_S) == 1.0

    def test_row_density(self):
        assert sylk_row_density(_S) == 2.0

    def test_row_density_avg(self):
        assert sylk_row_density_avg(_S) == 1.0

    def test_row_density_variance(self):
        assert sylk_row_density_variance(_S) == 0.0

    def test_row_fill_rate(self):
        assert sylk_row_fill_rate(_S) == 1.0

    def test_row_span(self):
        assert sylk_row_span(_S) == 2

    def test_string_cell_count(self):
        assert sylk_string_cell_count(_S) == 3

    def test_string_column_count(self):
        assert sylk_string_column_count(_S) == 2

    def test_string_density(self):
        assert sylk_string_density(_S) == 0.75

    def test_string_length_sum(self):
        assert sylk_string_length_sum(_S) == 14

    def test_string_value_count(self):
        assert sylk_string_value_count(_S) == 3

    def test_text_cell_ratio(self):
        assert sylk_text_cell_ratio(_S) == 0.75

    def test_total_cells(self):
        assert sylk_total_cells(_S) == 4

    def test_total_string_length(self):
        assert sylk_total_string_length(_S) == 16

    def test_total_sum(self):
        assert sylk_total_sum(_S) == 42.0

    def test_unique_cell_value_count(self):
        assert sylk_unique_cell_value_count(_S) == 4

    def test_unique_column_count(self):
        assert sylk_unique_column_count(_S) == 2

    def test_unique_row_count(self):
        assert sylk_unique_row_count(_S) == 2

    def test_unique_value_count(self):
        assert sylk_unique_value_count(_S) == 4

    def test_unique_values_col1(self):
        vals = sylk_unique_values(_S, 1)
        assert "Alpha" in vals
        assert "Name" in vals

    def test_value_sum(self):
        assert sylk_value_sum(_S) == 42.0

    def test_value_type_variety(self):
        assert sylk_value_type_variety(_S) == 2

    def test_value_variance(self):
        assert sylk_value_variance(_S) == 0.0

    # --- boolean analytics ---

    def test_has_empty_cells_false(self):
        assert sylk_has_empty_cells(_S) is False

    def test_has_empty_rows_false(self):
        assert sylk_has_empty_rows(_S) is False

    def test_has_header_true(self):
        assert sylk_has_header(_S) is True

    def test_has_multi_col_rows_true(self):
        assert sylk_has_multi_col_rows(_S) is True

    def test_has_numeric_cells_true(self):
        assert sylk_has_numeric_cells(_S) is True

    def test_has_only_numeric_false(self):
        assert sylk_has_only_numeric(_S) is False

    def test_has_string_cells_true(self):
        assert sylk_has_string_cells(_S) is True

    def test_has_string_cols_true(self):
        assert sylk_has_string_cols(_S) is True

    def test_is_all_numeric_false(self):
        assert sylk_is_all_numeric(_S) is False

    def test_is_empty_false(self):
        assert sylk_is_empty(_S) is False

    def test_is_multi_row_true(self):
        assert sylk_is_multi_row(_S) is True

    def test_is_rectangular_true(self):
        assert sylk_is_rectangular(_S) is True

    def test_is_single_column_false(self):
        assert sylk_is_single_column(_S) is False

    def test_is_single_row_false(self):
        assert sylk_is_single_row(_S) is False

    def test_is_square_true(self):
        assert sylk_is_square(_S) is True

    def test_is_wider_than_tall_false(self):
        assert sylk_is_wider_than_tall(_S) is False

    def test_string_cells_exceed_numeric_true(self):
        assert sylk_string_cells_exceed_numeric(_S) is True

    # --- NDJSON roundtrip ---

    def test_ndjson_roundtrip(self, tmp_path):
        out = tmp_path / "sylk_analytics.ndjson"
        records = [
            {"fn": "total_cells", "value": sylk_total_cells(_S)},
            {"fn": "numeric_sum", "value": sylk_numeric_sum(_S)},
            {"fn": "string_cell_count", "value": sylk_string_cell_count(_S)},
            {"fn": "row_span", "value": sylk_row_span(_S)},
            {"fn": "data_density", "value": sylk_data_density(_S)},
        ]
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == 5
        assert loaded[0]["value"] == 4
        assert loaded[1]["value"] == 42.0
        assert loaded[2]["value"] == 3
        assert loaded[3]["value"] == 2
        assert loaded[4]["value"] == 1.0
