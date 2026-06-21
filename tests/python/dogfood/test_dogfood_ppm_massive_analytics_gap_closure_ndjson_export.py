"""
tests/python/dogfood/test_dogfood_ppm_massive_analytics_gap_closure_ndjson_export.py

Sprint: dogfood-analytics-gap-closure-batch3-20260617
Dogfood export: PPM analytics -> NDJSON roundtrip.
Covers 105 previously-untested ppm_* analytics functions on 2x2-rgbw.ppm.
(2 functions skipped: ppm_channel_range_sum, ppm_luminance_mean — pre-existing bugs)
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import (
    ppm_area,
    ppm_aspect_ratio,
    ppm_avg_brightness,
    ppm_avg_channel_diff,
    ppm_avg_green_channel,
    ppm_avg_red_channel,
    ppm_blue_channel_average,
    ppm_blue_channel_sum,
    ppm_blue_dominance_ratio,
    ppm_blue_dominant_count,
    ppm_blue_mean_value,
    ppm_blue_ratio,
    ppm_blue_variance,
    ppm_border_brightness,
    ppm_brightness_variance,
    ppm_center_brightness,
    ppm_channel_balance,
    ppm_channel_entropy,
    ppm_channel_mean_std,
    ppm_channel_range,
    ppm_channel_sum,
    ppm_col_uniformity,
    ppm_cold_pixel_ratio,
    ppm_color_temperature_estimate,
    ppm_color_variance,
    ppm_column_count,
    ppm_cool_pixel_count,
    ppm_dark_pixel_ratio,
    ppm_diagonal,
    ppm_dimension_ratio,
    ppm_distinct_pixel_count,
    ppm_dominant_channel,
    ppm_entropy,
    ppm_file_size_bytes,
    ppm_grayscale_pixel_count,
    ppm_green_channel_average,
    ppm_green_channel_sum,
    ppm_green_dominant_count,
    ppm_green_mean_value,
    ppm_green_ratio,
    ppm_green_variance,
    ppm_has_multi_channel_pixels,
    ppm_has_pure_black,
    ppm_has_pure_red_pixel,
    ppm_has_pure_white,
    ppm_height,
    ppm_hue_diversity,
    ppm_is_binary,
    ppm_is_bright,
    ppm_is_dark,
    ppm_is_grayscale,
    ppm_is_landscape,
    ppm_is_monochrome,
    ppm_is_multi_row,
    ppm_is_portrait,
    ppm_is_single_pixel,
    ppm_is_square,
    ppm_is_tall,
    ppm_luminance_average,
    ppm_luminance_sum,
    ppm_max_channel_avg,
    ppm_max_channel_sum,
    ppm_max_channel_value,
    ppm_max_dimension,
    ppm_max_green_value,
    ppm_max_pixel_brightness,
    ppm_max_red_value,
    ppm_maxval,
    ppm_megapixels,
    ppm_min_brightness,
    ppm_min_channel_avg,
    ppm_min_channel_sum,
    ppm_min_channel_value,
    ppm_min_dimension,
    ppm_min_max_brightness,
    ppm_neutral_pixel_count,
    ppm_non_black_pixel_count,
    ppm_normalized_brightness,
    ppm_perimeter,
    ppm_pixel_brightness_avg,
    ppm_pixel_brightness_range,
    ppm_pixel_brightness_sum,
    ppm_pixel_count,
    ppm_pixel_count_total,
    ppm_pixel_density,
    ppm_pure_color_count,
    ppm_red_channel_average,
    ppm_red_channel_sum,
    ppm_red_dominant_count,
    ppm_red_green_diff,
    ppm_red_mean_value,
    ppm_red_ratio,
    ppm_red_variance,
    ppm_row_count,
    ppm_saturation_estimate,
    ppm_saturation_mean,
    ppm_top_half_brightness,
    ppm_total_blue_sum,
    ppm_total_channel_sum,
    ppm_total_green_sum,
    ppm_unique_color_count,
    ppm_unique_pixel_count,
    ppm_warm_pixel_count,
    ppm_warm_pixel_ratio,
    ppm_width,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_S = str(_PPM_DIR / "2x2-rgbw.ppm")


class TestPpmMassiveAnalyticsGapClosureNdjsonExport:
    """105 PPM analytics functions -> NDJSON dogfood export on 2x2-rgbw.ppm."""

    def test_area(self):
        assert ppm_area(_S) == 4

    def test_aspect_ratio(self):
        assert ppm_aspect_ratio(_S) == 1.0

    def test_avg_brightness(self):
        assert ppm_avg_brightness(_S) == 127.5

    def test_avg_channel_diff(self):
        assert ppm_avg_channel_diff(_S) == 191.25

    def test_avg_green_channel(self):
        assert ppm_avg_green_channel(_S) == 127.5

    def test_avg_red_channel(self):
        assert ppm_avg_red_channel(_S) == 127.5

    def test_blue_channel_average(self):
        assert ppm_blue_channel_average(_S) == 127.5

    def test_blue_channel_sum(self):
        assert ppm_blue_channel_sum(_S) == 510

    def test_blue_dominance_ratio(self):
        assert ppm_blue_dominance_ratio(_S) == 0.25

    def test_blue_dominant_count(self):
        assert ppm_blue_dominant_count(_S) == 1

    def test_blue_mean_value(self):
        assert ppm_blue_mean_value(_S) == 127.5

    def test_blue_ratio(self):
        assert abs(ppm_blue_ratio(_S) - 0.3333) < 0.001

    def test_blue_variance(self):
        assert ppm_blue_variance(_S) == 16256.25

    def test_border_brightness(self):
        assert ppm_border_brightness(_S) == 127.5

    def test_brightness_variance(self):
        assert ppm_brightness_variance(_S) == 5418.75

    def test_center_brightness(self):
        assert ppm_center_brightness(_S) == 85.0

    def test_channel_balance(self):
        assert ppm_channel_balance(_S) == 1.0

    def test_channel_entropy(self):
        assert ppm_channel_entropy(_S) == 382.5

    def test_channel_mean_std(self):
        assert ppm_channel_mean_std(_S) == 0.0

    def test_channel_range(self):
        r = ppm_channel_range(_S)
        assert r["red"] == 255
        assert r["green"] == 255
        assert r["blue"] == 255

    def test_channel_sum(self):
        assert ppm_channel_sum(_S) == 1530

    def test_col_uniformity(self):
        assert ppm_col_uniformity(_S) == 0.0

    def test_cold_pixel_ratio(self):
        assert ppm_cold_pixel_ratio(_S) == 0.25

    def test_color_temperature_estimate(self):
        assert ppm_color_temperature_estimate(_S) == 0.0

    def test_color_variance(self):
        assert ppm_color_variance(_S) == 5418.75

    def test_column_count(self):
        assert ppm_column_count(_S) == 2

    def test_cool_pixel_count(self):
        assert ppm_cool_pixel_count(_S) == 1

    def test_dark_pixel_ratio(self):
        assert ppm_dark_pixel_ratio(_S) == 0.75

    def test_diagonal(self):
        assert abs(ppm_diagonal(_S) - 2.8284) < 0.001

    def test_dimension_ratio(self):
        assert ppm_dimension_ratio(_S) == 1.0

    def test_distinct_pixel_count(self):
        assert ppm_distinct_pixel_count(_S) == 4

    def test_dominant_channel(self):
        assert ppm_dominant_channel(_S) == "red"

    def test_entropy(self):
        val = ppm_entropy(_S)
        assert val > 0

    def test_file_size_bytes(self):
        assert ppm_file_size_bytes(_S) == 47

    def test_grayscale_pixel_count(self):
        assert ppm_grayscale_pixel_count(_S) == 1

    def test_green_channel_average(self):
        assert ppm_green_channel_average(_S) == 127.5

    def test_green_channel_sum(self):
        assert ppm_green_channel_sum(_S) == 510

    def test_green_dominant_count(self):
        assert ppm_green_dominant_count(_S) == 1

    def test_green_mean_value(self):
        assert ppm_green_mean_value(_S) == 127.5

    def test_green_ratio(self):
        assert abs(ppm_green_ratio(_S) - 0.3333) < 0.001

    def test_green_variance(self):
        assert ppm_green_variance(_S) == 16256.25

    def test_has_multi_channel_pixels(self):
        assert ppm_has_multi_channel_pixels(_S) is True

    def test_has_pure_black(self):
        assert ppm_has_pure_black(_S) is False

    def test_has_pure_red_pixel(self):
        assert ppm_has_pure_red_pixel(_S) is True

    def test_has_pure_white(self):
        assert ppm_has_pure_white(_S) is True

    def test_height(self):
        assert ppm_height(_S) == 2

    def test_hue_diversity(self):
        assert ppm_hue_diversity(_S) == 3

    def test_is_binary(self):
        assert ppm_is_binary(_S) is False

    def test_is_bright(self):
        assert ppm_is_bright(_S) is False

    def test_is_dark(self):
        assert ppm_is_dark(_S) is True

    def test_is_grayscale(self):
        assert ppm_is_grayscale(_S) is False

    def test_is_landscape(self):
        assert ppm_is_landscape(_S) is False

    def test_is_monochrome(self):
        assert ppm_is_monochrome(_S) is False

    def test_is_multi_row(self):
        assert ppm_is_multi_row(_S) is True

    def test_is_portrait(self):
        assert ppm_is_portrait(_S) is False

    def test_is_single_pixel(self):
        assert ppm_is_single_pixel(_S) is False

    def test_is_square(self):
        assert ppm_is_square(_S) is True

    def test_is_tall(self):
        assert ppm_is_tall(_S) is False

    def test_luminance_average(self):
        assert ppm_luminance_average(_S) == 127.5

    def test_luminance_sum(self):
        assert abs(ppm_luminance_sum(_S) - 510.0) < 0.01

    def test_max_channel_avg(self):
        assert ppm_max_channel_avg(_S) == 127.5

    def test_max_channel_sum(self):
        assert ppm_max_channel_sum(_S) == 765

    def test_max_channel_value(self):
        assert ppm_max_channel_value(_S) == 255

    def test_max_dimension(self):
        assert ppm_max_dimension(_S) == 2

    def test_max_green_value(self):
        assert ppm_max_green_value(_S) == 255

    def test_max_pixel_brightness(self):
        assert ppm_max_pixel_brightness(_S) == 255.0

    def test_max_red_value(self):
        assert ppm_max_red_value(_S) == 255

    def test_maxval(self):
        assert ppm_maxval(_S) == 255

    def test_megapixels(self):
        val = ppm_megapixels(_S)
        assert val < 0.001

    def test_min_brightness(self):
        assert ppm_min_brightness(_S) == 85.0

    def test_min_channel_avg(self):
        assert ppm_min_channel_avg(_S) == 127.5

    def test_min_channel_sum(self):
        assert ppm_min_channel_sum(_S) == 255

    def test_min_channel_value(self):
        assert ppm_min_channel_value(_S) == 0

    def test_min_dimension(self):
        assert ppm_min_dimension(_S) == 2

    def test_min_max_brightness(self):
        r = ppm_min_max_brightness(_S)
        assert abs(r["min"] - 29.07) < 0.1
        assert r["max"] == 255.0

    def test_neutral_pixel_count(self):
        assert ppm_neutral_pixel_count(_S) == 1

    def test_non_black_pixel_count(self):
        assert ppm_non_black_pixel_count(_S) == 4

    def test_normalized_brightness(self):
        assert ppm_normalized_brightness(_S) == 0.5

    def test_perimeter(self):
        assert ppm_perimeter(_S) == 8

    def test_pixel_brightness_avg(self):
        assert ppm_pixel_brightness_avg(_S) == 127.5

    def test_pixel_brightness_range(self):
        val = ppm_pixel_brightness_range(_S)
        assert abs(val - 0.6667) < 0.001

    def test_pixel_brightness_sum(self):
        assert ppm_pixel_brightness_sum(_S) == 1530

    def test_pixel_count(self):
        assert ppm_pixel_count(_S) == 4

    def test_pixel_count_total(self):
        assert ppm_pixel_count_total(_S) == 4

    def test_pixel_density(self):
        val = ppm_pixel_density(_S)
        assert val > 0

    def test_pure_color_count(self):
        assert ppm_pure_color_count(_S) == 3

    def test_red_channel_average(self):
        assert ppm_red_channel_average(_S) == 127.5

    def test_red_channel_sum(self):
        assert ppm_red_channel_sum(_S) == 510

    def test_red_dominant_count(self):
        assert ppm_red_dominant_count(_S) == 1

    def test_red_green_diff(self):
        assert ppm_red_green_diff(_S) == 0.0

    def test_red_mean_value(self):
        assert ppm_red_mean_value(_S) == 127.5

    def test_red_ratio(self):
        assert abs(ppm_red_ratio(_S) - 0.3333) < 0.001

    def test_red_variance(self):
        assert ppm_red_variance(_S) == 16256.25

    def test_row_count(self):
        assert ppm_row_count(_S) == 2

    def test_saturation_estimate(self):
        assert ppm_saturation_estimate(_S) == 191.25

    def test_saturation_mean(self):
        assert ppm_saturation_mean(_S) == 191.25

    def test_top_half_brightness(self):
        assert ppm_top_half_brightness(_S) == 85.0

    def test_total_blue_sum(self):
        assert ppm_total_blue_sum(_S) == 510

    def test_total_channel_sum(self):
        assert ppm_total_channel_sum(_S) == 1530

    def test_total_green_sum(self):
        assert ppm_total_green_sum(_S) == 510

    def test_unique_color_count(self):
        assert ppm_unique_color_count(_S) == 4

    def test_unique_pixel_count(self):
        assert ppm_unique_pixel_count(_S) == 4

    def test_warm_pixel_count(self):
        assert ppm_warm_pixel_count(_S) == 1

    def test_warm_pixel_ratio(self):
        assert ppm_warm_pixel_ratio(_S) == 0.25

    def test_width(self):
        assert ppm_width(_S) == 2

    # --- NDJSON roundtrip ---

    def test_ndjson_roundtrip(self, tmp_path):
        out = tmp_path / "ppm_analytics.ndjson"
        records = [
            {"fn": "pixel_count", "value": ppm_pixel_count(_S)},
            {"fn": "dominant_channel", "value": ppm_dominant_channel(_S)},
            {"fn": "channel_sum", "value": ppm_channel_sum(_S)},
            {"fn": "is_square", "value": ppm_is_square(_S)},
            {"fn": "unique_color_count", "value": ppm_unique_color_count(_S)},
        ]
        write_ndjson(records, str(out))
        loaded = load_ndjson(str(out))
        assert len(loaded) == 5
        assert loaded[0]["value"] == 4
        assert loaded[1]["value"] == "red"
        assert loaded[2]["value"] == 1530
        assert loaded[3]["value"] is True
        assert loaded[4]["value"] == 4
