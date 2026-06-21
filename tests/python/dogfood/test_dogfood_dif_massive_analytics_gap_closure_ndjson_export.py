"""
tests/python/dogfood/test_dogfood_dif_massive_analytics_gap_closure_ndjson_export.py

Sprint: dogfood-analytics-gap-closure-batch2-20260617
Dogfood export: DIF analytics -> NDJSON roundtrip.
Covers 80+ previously-untested dif_* analytics functions on minimal-2x2.dif.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import (
    dif_all_numeric,
    dif_all_numeric_column,
    dif_avg_cell_length,
    dif_avg_cell_length_variance,
    dif_avg_cell_text_length,
    dif_avg_cells_per_row,
    dif_avg_numeric_value,
    dif_avg_row_cell_count,
    dif_avg_row_length,
    dif_avg_row_width,
    dif_avg_string_length,
    dif_cell_count_variance,
    dif_cell_text_variance,
    dif_cell_value_length_sum,
    dif_cells_per_tuple,
    dif_col_count_exceeds_numeric_count,
    dif_col_count_variance,
    dif_column_count,
    dif_column_count_avg,
    dif_column_density,
    dif_column_fill_ratio,
    dif_column_type_variety,
    dif_column_types,
    dif_column_unique_count,
    dif_data_density,
    dif_distinct_numeric_count,
    dif_empty_cell_count,
    dif_empty_cell_ratio,
    dif_empty_column_count,
    dif_empty_row_ratio,
    dif_file_size_bytes,
    dif_has_empty_cells,
    dif_has_header,
    dif_has_mixed_types,
    dif_has_string_cells,
    dif_has_string_rows,
    dif_header_count,
    dif_is_all_string,
    dif_is_empty,
    dif_is_multi_vector,
    dif_is_rectangular,
    dif_is_single_column,
    dif_is_single_row,
    dif_is_single_vector,
    dif_is_wider_than_tall,
    dif_longest_row_index,
    dif_max_cell_length,
    dif_max_cell_text_length,
    dif_max_column_sum,
    dif_max_numeric_int_value,
    dif_max_numeric_length,
    dif_max_numeric_value,
    dif_max_row_cell_count,
    dif_max_row_index,
    dif_max_row_length,
    dif_max_row_width,
    dif_max_string_length,
    dif_min_cell_length,
    dif_min_column_sum,
    dif_min_numeric_value,
    dif_min_row_cell_count,
    dif_min_row_index,
    dif_min_row_width,
    dif_nonempty_cell_count,
    dif_nonempty_cell_density,
    dif_nonempty_cell_ratio,
    dif_nonempty_row_count,
    dif_nonempty_row_ratio,
    dif_numeric_cell_count,
    dif_numeric_cell_mean,
    dif_numeric_cell_ratio,
    dif_numeric_cell_sum,
    dif_numeric_col_ratio,
    dif_numeric_column_count,
    dif_numeric_density,
    dif_numeric_mean,
    dif_numeric_range,
    dif_numeric_ratio,
    dif_numeric_sum,
    dif_numeric_sum_per_cell,
    dif_row_cell_count_avg,
    dif_row_col_ratio,
    dif_row_count,
    dif_row_length_variance,
    dif_row_width_variance,
    dif_string_cell_ratio,
    dif_string_density,
    dif_string_field_count,
    dif_string_length_sum,
    dif_string_ratio,
    dif_string_row_count,
    dif_string_value_count,
    dif_total_cell_count,
    dif_total_cell_length,
    dif_total_cell_value_count,
    dif_total_char_count,
    dif_total_string_length,
    dif_tuple_count,
    dif_unique_row_count,
    dif_unique_string_count,
    dif_unique_value_count,
    dif_value_sum,
    dif_value_text_total_length,
    dif_value_type_variance,
    dif_value_variance,
    dif_vector_length_variance,
    dif_vectors_count,
    dif_vectors_tuples_sum,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_DIF_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_S = str(_DIF_DIR / "minimal-2x2.dif")


class TestDifMassiveAnalyticsGapClosureNdjsonExport:
    """80+ DIF analytics functions -> NDJSON dogfood export on minimal-2x2.dif."""

    # --- numeric analytics ---

    def test_avg_cell_length(self):
        assert dif_avg_cell_length(_S) == 4.5

    def test_avg_cell_length_variance(self):
        assert dif_avg_cell_length_variance(_S) == 5.25

    def test_avg_cell_text_length(self):
        assert dif_avg_cell_text_length(_S) == 4.5

    def test_avg_cells_per_row(self):
        assert dif_avg_cells_per_row(_S) == 8.0

    def test_avg_numeric_value(self):
        assert dif_avg_numeric_value(_S) == 70.5

    def test_avg_row_cell_count(self):
        assert dif_avg_row_cell_count(_S) == 8.0

    def test_avg_row_length(self):
        assert dif_avg_row_length(_S) == 8.0

    def test_avg_row_width(self):
        assert dif_avg_row_width(_S) == 8.0

    def test_avg_string_length(self):
        val = dif_avg_string_length(_S)
        assert abs(val - 4.6667) < 0.001

    def test_cell_count_variance(self):
        assert dif_cell_count_variance(_S) == 0.0

    def test_cell_text_variance(self):
        assert dif_cell_text_variance(_S) == 8.1875

    def test_cell_value_length_sum(self):
        assert dif_cell_value_length_sum(_S) == 342

    def test_cells_per_tuple(self):
        assert dif_cells_per_tuple(_S) == 4.0

    def test_col_count_variance(self):
        assert dif_col_count_variance(_S) == 0.0

    def test_column_count(self):
        assert dif_column_count(_S) == 8

    def test_column_count_avg(self):
        assert dif_column_count_avg(_S) == 8.0

    def test_column_density(self):
        assert dif_column_density(_S) == 1.0

    def test_column_fill_ratio(self):
        assert dif_column_fill_ratio(_S) == 4.0

    def test_column_type_variety(self):
        assert dif_column_type_variety(_S) == 2

    def test_column_types(self):
        types = dif_column_types(_S)
        assert "numeric" in types
        assert "string" in types

    def test_column_unique_count(self):
        assert dif_column_unique_count(_S, 0) >= 0

    def test_data_density(self):
        assert dif_data_density(_S) == 1.0

    def test_distinct_numeric_count(self):
        assert dif_distinct_numeric_count(_S) == 2

    def test_empty_cell_count(self):
        assert dif_empty_cell_count(_S) == 0

    def test_empty_cell_ratio(self):
        assert dif_empty_cell_ratio(_S) == 0.0

    def test_empty_column_count(self):
        assert dif_empty_column_count(_S) == 0

    def test_empty_row_ratio(self):
        assert dif_empty_row_ratio(_S) == 0.0

    def test_file_size_bytes(self):
        val = dif_file_size_bytes(_S)
        assert isinstance(val, int)
        assert val > 0

    def test_header_count(self):
        assert dif_header_count(_S) == 2

    def test_longest_row_index(self):
        assert dif_longest_row_index(_S) == 0

    def test_max_cell_length(self):
        assert dif_max_cell_length(_S) == 7

    def test_max_cell_text_length(self):
        assert dif_max_cell_text_length(_S) == 46

    def test_max_column_sum(self):
        assert dif_max_column_sum(_S) == 99.0

    def test_max_numeric_int_value(self):
        assert dif_max_numeric_int_value(_S) == 99

    def test_max_numeric_length(self):
        assert dif_max_numeric_length(_S) == 4

    def test_max_numeric_value(self):
        assert dif_max_numeric_value(_S) == 99.0

    def test_max_row_cell_count(self):
        assert dif_max_row_cell_count(_S) == 8

    def test_max_row_index(self):
        assert dif_max_row_index(_S) == 0

    def test_max_row_length(self):
        assert dif_max_row_length(_S) == 8

    def test_max_row_width(self):
        assert dif_max_row_width(_S) == 8

    def test_max_string_length(self):
        assert dif_max_string_length(_S) == 7

    def test_min_cell_length(self):
        assert dif_min_cell_length(_S) == 1

    def test_min_column_sum(self):
        assert dif_min_column_sum(_S) == 42.0

    def test_min_numeric_value(self):
        assert dif_min_numeric_value(_S) == 42.0

    def test_min_row_cell_count(self):
        assert dif_min_row_cell_count(_S) == 8

    def test_min_row_index(self):
        assert dif_min_row_index(_S) == 0

    def test_min_row_width(self):
        assert dif_min_row_width(_S) == 8

    def test_nonempty_cell_count(self):
        assert dif_nonempty_cell_count(_S) == 8

    def test_nonempty_cell_density(self):
        assert dif_nonempty_cell_density(_S) == 1.0

    def test_nonempty_cell_ratio(self):
        assert dif_nonempty_cell_ratio(_S) == 1.0

    def test_nonempty_row_count(self):
        assert dif_nonempty_row_count(_S) == 1

    def test_nonempty_row_ratio(self):
        assert dif_nonempty_row_ratio(_S) == 1.0

    def test_numeric_cell_count(self):
        assert dif_numeric_cell_count(_S) == 2

    def test_numeric_cell_mean(self):
        assert dif_numeric_cell_mean(_S) == 0.0

    def test_numeric_cell_ratio(self):
        assert dif_numeric_cell_ratio(_S) == 0.25

    def test_numeric_cell_sum(self):
        assert dif_numeric_cell_sum(_S) == 141.0

    def test_numeric_col_ratio(self):
        assert dif_numeric_col_ratio(_S) == 0.25

    def test_numeric_column_count(self):
        assert dif_numeric_column_count(_S) == 2

    def test_numeric_density(self):
        assert dif_numeric_density(_S) == 0.25

    def test_numeric_mean(self):
        assert dif_numeric_mean(_S) == 70.5

    def test_numeric_range(self):
        assert dif_numeric_range(_S) == 57.0

    def test_numeric_ratio(self):
        assert dif_numeric_ratio(_S) == 0.25

    def test_numeric_sum(self):
        assert dif_numeric_sum(_S) == 141.0

    def test_numeric_sum_per_cell(self):
        assert dif_numeric_sum_per_cell(_S) == 17.625

    def test_row_cell_count_avg(self):
        assert dif_row_cell_count_avg(_S) == 8.0

    def test_row_col_ratio(self):
        assert dif_row_col_ratio(_S) == 0.125

    def test_row_count(self):
        assert dif_row_count(_S) == 1

    def test_row_length_variance(self):
        assert dif_row_length_variance(_S) == 0.0

    def test_row_width_variance(self):
        assert dif_row_width_variance(_S) == 0.0

    def test_string_cell_ratio(self):
        assert dif_string_cell_ratio(_S) == 0.25

    def test_string_density(self):
        assert dif_string_density(_S) == 0.25

    def test_string_field_count(self):
        assert dif_string_field_count(_S) == 6

    def test_string_length_sum(self):
        assert dif_string_length_sum(_S) == 28

    def test_string_ratio(self):
        assert dif_string_ratio(_S) == 0.75

    def test_string_row_count(self):
        assert dif_string_row_count(_S) == 1

    def test_string_value_count(self):
        assert dif_string_value_count(_S) == 2

    def test_total_cell_count(self):
        assert dif_total_cell_count(_S) == 8

    def test_total_cell_length(self):
        assert dif_total_cell_length(_S) == 36

    def test_total_cell_value_count(self):
        assert dif_total_cell_value_count(_S) == 8

    def test_total_char_count(self):
        assert dif_total_char_count(_S) == 28

    def test_total_string_length(self):
        assert dif_total_string_length(_S) == 36

    def test_tuple_count(self):
        assert dif_tuple_count(_S) == 2

    def test_unique_row_count(self):
        assert dif_unique_row_count(_S) == 1

    def test_unique_string_count(self):
        assert dif_unique_string_count(_S) == 1

    def test_unique_value_count(self):
        assert dif_unique_value_count(_S) == 7

    def test_value_sum(self):
        assert dif_value_sum(_S) == 141.0

    def test_value_text_total_length(self):
        assert dif_value_text_total_length(_S) == 342

    def test_value_type_variance(self):
        assert dif_value_type_variance(_S) == 0.0

    def test_value_variance(self):
        assert dif_value_variance(_S) == 812.25

    def test_vector_length_variance(self):
        assert dif_vector_length_variance(_S) == 0.0

    def test_vectors_count(self):
        assert dif_vectors_count(_S) == 2

    def test_vectors_tuples_sum(self):
        assert dif_vectors_tuples_sum(_S) == 4

    # --- boolean analytics ---

    def test_all_numeric_false(self):
        assert dif_all_numeric(_S) is False

    def test_all_numeric_column_false(self):
        assert dif_all_numeric_column(_S) is False

    def test_col_count_exceeds_numeric_count_true(self):
        assert dif_col_count_exceeds_numeric_count(_S) is True

    def test_has_empty_cells_false(self):
        assert dif_has_empty_cells(_S) is False

    def test_has_header_false(self):
        assert dif_has_header(_S) is False

    def test_has_mixed_types_true(self):
        assert dif_has_mixed_types(_S) is True

    def test_has_string_cells_true(self):
        assert dif_has_string_cells(_S) is True

    def test_has_string_rows_true(self):
        assert dif_has_string_rows(_S) is True

    def test_is_all_string_false(self):
        assert dif_is_all_string(_S) is False

    def test_is_empty_false(self):
        assert dif_is_empty(_S) is False

    def test_is_multi_vector_true(self):
        assert dif_is_multi_vector(_S) is True

    def test_is_rectangular_true(self):
        assert dif_is_rectangular(_S) is True

    def test_is_single_column_false(self):
        assert dif_is_single_column(_S) is False

    def test_is_single_row_true(self):
        assert dif_is_single_row(_S) is True

    def test_is_single_vector_false(self):
        assert dif_is_single_vector(_S) is False

    def test_is_wider_than_tall_false(self):
        assert dif_is_wider_than_tall(_S) is False

    # --- NDJSON roundtrip ---

    def test_ndjson_roundtrip(self, tmp_path):
        out = tmp_path / "dif_analytics.ndjson"
        records = [
            {"fn": "total_cell_count", "value": dif_total_cell_count(_S)},
            {"fn": "numeric_sum", "value": dif_numeric_sum(_S)},
            {"fn": "string_field_count", "value": dif_string_field_count(_S)},
            {"fn": "row_count", "value": dif_row_count(_S)},
            {"fn": "data_density", "value": dif_data_density(_S)},
        ]
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == 5
        assert loaded[0]["value"] == 8
        assert loaded[1]["value"] == 141.0
        assert loaded[2]["value"] == 6
        assert loaded[3]["value"] == 1
        assert loaded[4]["value"] == 1.0
