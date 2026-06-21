"""
tests/python/dogfood/test_dogfood_pgm_massive_analytics_gap_closure_ndjson_export.py

Sprint: dogfood-analytics-gap-closure-batch3-20260617
Dogfood export: PGM analytics -> NDJSON roundtrip.
Covers 106 previously-untested pgm_* analytics functions on 2x2-gradient.pgm.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import (
    pgm_above_average_count,
    pgm_above_mean_ratio,
    pgm_area,
    pgm_aspect_ratio,
    pgm_average_brightness,
    pgm_avg_pixel_per_row,
    pgm_avg_row_brightness,
    pgm_below_average_count,
    pgm_below_midpoint_count,
    pgm_border_mean,
    pgm_bottom_half_avg,
    pgm_bottom_row_mean,
    pgm_bright_pixel_count,
    pgm_bright_pixel_ratio,
    pgm_brightness_histogram,
    pgm_brightness_quartiles,
    pgm_brightness_range,
    pgm_brightness_ratio,
    pgm_brightness_variance,
    pgm_center_brightness,
    pgm_center_pixel_value,
    pgm_col_brightness_variance,
    pgm_col_uniformity,
    pgm_column_count,
    pgm_column_mean,
    pgm_column_mean_max,
    pgm_contrast_range,
    pgm_contrast_ratio,
    pgm_dark_pixel_count,
    pgm_dark_pixel_ratio,
    pgm_diagonal,
    pgm_dimension_ratio,
    pgm_dynamic_range,
    pgm_edge_pixel_mean,
    pgm_entropy,
    pgm_file_size_bytes,
    pgm_full_white_pixel_count,
    pgm_gradient_magnitude,
    pgm_has_any_saturated,
    pgm_has_any_zero,
    pgm_has_only_extremes,
    pgm_height,
    pgm_highlight_count,
    pgm_is_all_bright,
    pgm_is_all_dark,
    pgm_is_bright,
    pgm_is_high_contrast,
    pgm_is_landscape,
    pgm_is_multi_row,
    pgm_is_portrait,
    pgm_is_single_pixel,
    pgm_is_square,
    pgm_is_tall,
    pgm_is_uniform,
    pgm_is_wide,
    pgm_left_column_mean,
    pgm_max_dimension,
    pgm_max_pixel_value,
    pgm_maxval,
    pgm_maxval_exceeds_avg,
    pgm_mean_brightness,
    pgm_median_brightness,
    pgm_median_pixel_value,
    pgm_megapixels,
    pgm_mid_pixel_ratio,
    pgm_midpoint_gray,
    pgm_midtone_pixel_count,
    pgm_min_brightness,
    pgm_min_dimension,
    pgm_min_pixel_value,
    pgm_mode_pixel_value,
    pgm_nonzero_pixel_count,
    pgm_nonzero_pixel_ratio,
    pgm_normalized_mean,
    pgm_percentile_value,
    pgm_perimeter,
    pgm_pixel_count,
    pgm_pixel_density,
    pgm_pixel_density_ratio,
    pgm_pixel_entropy,
    pgm_pixel_median,
    pgm_pixel_quartile_count,
    pgm_pixel_range,
    pgm_pixel_sum,
    pgm_pixel_sum_normalized,
    pgm_pixel_value_range,
    pgm_pixel_value_variance,
    pgm_pixel_variance,
    pgm_right_column_mean,
    pgm_row_brightness_sum,
    pgm_row_brightness_variance,
    pgm_row_count,
    pgm_row_mean,
    pgm_saturated_pixel_count,
    pgm_saturated_pixel_ratio,
    pgm_shadow_pixel_count,
    pgm_standard_deviation,
    pgm_top_half_avg,
    pgm_top_row_mean,
    pgm_total_pixel_count,
    pgm_total_pixel_sum,
    pgm_unique_pixel_count,
    pgm_unique_value_count,
    pgm_width,
    pgm_width_exceeds_height,
    pgm_zero_pixel_count,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PGM_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_S = str(_PGM_DIR / "2x2-gradient.pgm")


class TestPgmMassiveAnalyticsGapClosureNdjsonExport:
    """106 PGM analytics functions -> NDJSON dogfood export on 2x2-gradient.pgm."""

    def test_above_average_count(self):
        assert pgm_above_average_count(_S) == 2

    def test_above_mean_ratio(self):
        assert pgm_above_mean_ratio(_S) == 0.5

    def test_area(self):
        assert pgm_area(_S) == 4

    def test_aspect_ratio(self):
        assert pgm_aspect_ratio(_S) == 1.0

    def test_average_brightness(self):
        assert pgm_average_brightness(_S) == 127.5

    def test_avg_pixel_per_row(self):
        assert pgm_avg_pixel_per_row(_S) == 127.5

    def test_avg_row_brightness(self):
        val = pgm_avg_row_brightness(_S)
        assert abs(val[0] - 42.5) < 0.01
        assert abs(val[1] - 212.5) < 0.01

    def test_below_average_count(self):
        assert pgm_below_average_count(_S) == 2

    def test_below_midpoint_count(self):
        assert pgm_below_midpoint_count(_S) == 2

    def test_border_mean(self):
        assert pgm_border_mean(_S) == 127.5

    def test_bottom_half_avg(self):
        assert pgm_bottom_half_avg(_S) == 212.5

    def test_bottom_row_mean(self):
        assert pgm_bottom_row_mean(_S) == 212.5

    def test_bright_pixel_count(self):
        assert pgm_bright_pixel_count(_S) == 2

    def test_bright_pixel_ratio(self):
        assert pgm_bright_pixel_ratio(_S) == 0.25

    def test_brightness_histogram(self):
        val = pgm_brightness_histogram(_S)
        assert len(val) == 4

    def test_brightness_quartiles(self):
        q = pgm_brightness_quartiles(_S)
        assert q["q25"] == 85
        assert q["q75"] == 255

    def test_brightness_range(self):
        assert pgm_brightness_range(_S) == 255

    def test_brightness_ratio(self):
        assert pgm_brightness_ratio(_S) == 0.5

    def test_brightness_variance(self):
        assert abs(pgm_brightness_variance(_S) - 9031.25) < 0.01

    def test_center_brightness(self):
        assert pgm_center_brightness(_S) == 0.0

    def test_center_pixel_value(self):
        assert pgm_center_pixel_value(_S) == 255

    def test_col_brightness_variance(self):
        assert abs(pgm_col_brightness_variance(_S) - 1806.25) < 0.01

    def test_col_uniformity(self):
        assert pgm_col_uniformity(_S) == 0.0

    def test_column_count(self):
        assert pgm_column_count(_S) == 2

    def test_column_mean(self):
        assert pgm_column_mean(_S) == 127.5

    def test_column_mean_max(self):
        assert pgm_column_mean_max(_S) == 170.0

    def test_contrast_range(self):
        assert pgm_contrast_range(_S) == 255

    def test_contrast_ratio(self):
        assert pgm_contrast_ratio(_S) == 1.0

    def test_dark_pixel_count(self):
        assert pgm_dark_pixel_count(_S) == 1

    def test_dark_pixel_ratio(self):
        assert pgm_dark_pixel_ratio(_S) == 0.25

    def test_diagonal(self):
        assert abs(pgm_diagonal(_S) - 2.8284) < 0.001

    def test_dimension_ratio(self):
        assert pgm_dimension_ratio(_S) == 1.0

    def test_dynamic_range(self):
        assert pgm_dynamic_range(_S) == 255

    def test_edge_pixel_mean(self):
        assert pgm_edge_pixel_mean(_S) == 127.5

    def test_entropy(self):
        assert pgm_entropy(_S) == 2.0

    def test_file_size_bytes(self):
        assert pgm_file_size_bytes(_S) == 29

    def test_full_white_pixel_count(self):
        assert pgm_full_white_pixel_count(_S) == 1

    def test_gradient_magnitude(self):
        assert pgm_gradient_magnitude(_S) == 85.0

    def test_has_any_saturated(self):
        assert pgm_has_any_saturated(_S) is True

    def test_has_any_zero(self):
        assert pgm_has_any_zero(_S) is True

    def test_has_only_extremes(self):
        assert pgm_has_only_extremes(_S) is False

    def test_height(self):
        assert pgm_height(_S) == 2

    def test_highlight_count(self):
        assert pgm_highlight_count(_S) == 2

    def test_is_all_bright(self):
        assert pgm_is_all_bright(_S) is False

    def test_is_all_dark(self):
        assert pgm_is_all_dark(_S) is False

    def test_is_bright(self):
        assert pgm_is_bright(_S) is False

    def test_is_high_contrast(self):
        assert pgm_is_high_contrast(_S) is True

    def test_is_landscape(self):
        assert pgm_is_landscape(_S) is False

    def test_is_multi_row(self):
        assert pgm_is_multi_row(_S) is True

    def test_is_portrait(self):
        assert pgm_is_portrait(_S) is False

    def test_is_single_pixel(self):
        assert pgm_is_single_pixel(_S) is False

    def test_is_square(self):
        assert pgm_is_square(_S) is True

    def test_is_tall(self):
        assert pgm_is_tall(_S) is False

    def test_is_uniform(self):
        assert pgm_is_uniform(_S) is False

    def test_is_wide(self):
        assert pgm_is_wide(_S) is False

    def test_left_column_mean(self):
        assert pgm_left_column_mean(_S) == 85.0

    def test_max_dimension(self):
        assert pgm_max_dimension(_S) == 2

    def test_max_pixel_value(self):
        assert pgm_max_pixel_value(_S) == 255

    def test_maxval(self):
        assert pgm_maxval(_S) == 255

    def test_maxval_exceeds_avg(self):
        assert pgm_maxval_exceeds_avg(_S) is True

    def test_mean_brightness(self):
        assert pgm_mean_brightness(_S) == 127.5

    def test_median_brightness(self):
        assert pgm_median_brightness(_S) == 127.5

    def test_median_pixel_value(self):
        assert pgm_median_pixel_value(_S) == 85

    def test_megapixels(self):
        val = pgm_megapixels(_S)
        assert val < 0.001

    def test_mid_pixel_ratio(self):
        assert pgm_mid_pixel_ratio(_S) == 0.5

    def test_midpoint_gray(self):
        assert pgm_midpoint_gray(_S) == 127

    def test_midtone_pixel_count(self):
        assert pgm_midtone_pixel_count(_S) == 2

    def test_min_brightness(self):
        assert pgm_min_brightness(_S) == 0

    def test_min_dimension(self):
        assert pgm_min_dimension(_S) == 2

    def test_min_pixel_value(self):
        assert pgm_min_pixel_value(_S) == 0

    def test_mode_pixel_value(self):
        assert pgm_mode_pixel_value(_S) == 0

    def test_nonzero_pixel_count(self):
        assert pgm_nonzero_pixel_count(_S) == 3

    def test_nonzero_pixel_ratio(self):
        assert pgm_nonzero_pixel_ratio(_S) == 0.75

    def test_normalized_mean(self):
        assert pgm_normalized_mean(_S) == 0.5

    def test_percentile_value(self):
        assert pgm_percentile_value(_S) == 170

    def test_perimeter(self):
        assert pgm_perimeter(_S) == 8

    def test_pixel_count(self):
        assert pgm_pixel_count(_S) == 4

    def test_pixel_density(self):
        val = pgm_pixel_density(_S)
        assert val > 0

    def test_pixel_density_ratio(self):
        assert pgm_pixel_density_ratio(_S) == 0.75

    def test_pixel_entropy(self):
        assert pgm_pixel_entropy(_S) == 2.0

    def test_pixel_median(self):
        assert pgm_pixel_median(_S) == 127.5

    def test_pixel_quartile_count(self):
        assert pgm_pixel_quartile_count(_S) == 4

    def test_pixel_range(self):
        assert pgm_pixel_range(_S) == 255

    def test_pixel_sum(self):
        assert pgm_pixel_sum(_S) == 510

    def test_pixel_sum_normalized(self):
        assert pgm_pixel_sum_normalized(_S) == 0.5

    def test_pixel_value_range(self):
        assert pgm_pixel_value_range(_S) == 255

    def test_pixel_value_variance(self):
        assert abs(pgm_pixel_value_variance(_S) - 9031.25) < 0.01

    def test_pixel_variance(self):
        assert abs(pgm_pixel_variance(_S) - 9031.25) < 0.01

    def test_right_column_mean(self):
        assert pgm_right_column_mean(_S) == 170.0

    def test_row_brightness_sum(self):
        assert pgm_row_brightness_sum(_S) == 340

    def test_row_brightness_variance(self):
        assert pgm_row_brightness_variance(_S) == 7225.0

    def test_row_count(self):
        assert pgm_row_count(_S) == 2

    def test_row_mean(self):
        assert pgm_row_mean(_S) == 127.5

    def test_saturated_pixel_count(self):
        assert pgm_saturated_pixel_count(_S) == 1

    def test_saturated_pixel_ratio(self):
        assert pgm_saturated_pixel_ratio(_S) == 0.25

    def test_shadow_pixel_count(self):
        assert pgm_shadow_pixel_count(_S) == 2

    def test_standard_deviation(self):
        assert abs(pgm_standard_deviation(_S) - 95.0328) < 0.01

    def test_top_half_avg(self):
        assert pgm_top_half_avg(_S) == 42.5

    def test_top_row_mean(self):
        assert pgm_top_row_mean(_S) == 42.5

    def test_total_pixel_count(self):
        assert pgm_total_pixel_count(_S) == 4

    def test_total_pixel_sum(self):
        assert pgm_total_pixel_sum(_S) == 510

    def test_unique_pixel_count(self):
        assert pgm_unique_pixel_count(_S) == 4

    def test_unique_value_count(self):
        assert pgm_unique_value_count(_S) == 4

    def test_width(self):
        assert pgm_width(_S) == 2

    def test_width_exceeds_height(self):
        assert pgm_width_exceeds_height(_S) is False

    def test_zero_pixel_count(self):
        assert pgm_zero_pixel_count(_S) == 1

    # --- NDJSON roundtrip ---

    def test_ndjson_roundtrip(self, tmp_path):
        out = tmp_path / "pgm_analytics.ndjson"
        records = [
            {"fn": "pixel_count", "value": pgm_pixel_count(_S)},
            {"fn": "mean_brightness", "value": pgm_mean_brightness(_S)},
            {"fn": "pixel_sum", "value": pgm_pixel_sum(_S)},
            {"fn": "width", "value": pgm_width(_S)},
            {"fn": "is_square", "value": pgm_is_square(_S)},
        ]
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == 5
        assert loaded[0]["value"] == 4
        assert loaded[1]["value"] == 127.5
        assert loaded[2]["value"] == 510
        assert loaded[3]["value"] == 2
        assert loaded[4]["value"] is True
