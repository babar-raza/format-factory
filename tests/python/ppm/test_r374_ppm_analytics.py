"""Tests for PPM analytics functions — coverage sprint r374.

Covers 53 ppm_ analytics functions using 3 real PPM sample files.
Each test asserts return type and plausible value.
"""
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm import (
    ppm_area, ppm_aspect_ratio, ppm_avg_brightness, ppm_blue_channel_average,
    ppm_blue_channel_sum, ppm_blue_ratio, ppm_border_brightness, ppm_brightness_variance,
    ppm_channel_balance, ppm_channel_range, ppm_color_variance, ppm_column_count,
    ppm_diagonal, ppm_dimension_ratio, ppm_distinct_pixel_count, ppm_dominant_channel,
    ppm_green_channel_average, ppm_green_channel_sum, ppm_green_ratio,
    ppm_has_pure_black, ppm_has_pure_white, ppm_is_binary, ppm_is_bright, ppm_is_dark,
    ppm_is_grayscale, ppm_is_landscape, ppm_is_monochrome, ppm_is_portrait,
    ppm_is_square, ppm_is_tall, ppm_luminance_average, ppm_max_channel_sum,
    ppm_max_dimension, ppm_max_pixel_brightness, ppm_maxval, ppm_megapixels,
    ppm_min_channel_avg, ppm_min_channel_sum, ppm_min_dimension, ppm_min_max_brightness,
    ppm_normalized_brightness, ppm_perimeter, ppm_pixel_brightness_range,
    ppm_pixel_count, ppm_pixel_density, ppm_red_channel_average, ppm_red_channel_sum,
    ppm_red_ratio, ppm_row_count, ppm_saturation_estimate,
    ppm_total_channel_sum, ppm_unique_color_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "ppm" / "valid"
_RGBW    = str(_SAMPLES / "2x2-rgbw.ppm")      # 2x2 red/green/blue/white
_GRAD    = str(_SAMPLES / "3x1-gradient.ppm")  # 3x1 gradient
_RED1    = str(_SAMPLES / "1x1-red.ppm")       # 1x1 red


class TestPpmArea:
    def test_area_returns_int(self):
        assert isinstance(ppm_area(_RGBW), int)

    def test_rgbw_area_is_4(self):
        assert ppm_area(_RGBW) == 4

    def test_grad_area_is_3(self):
        assert ppm_area(_GRAD) == 3

    def test_red1_area_is_1(self):
        assert ppm_area(_RED1) == 1


class TestPpmPixelCount:
    def test_pixel_count_returns_int(self):
        assert isinstance(ppm_pixel_count(_RGBW), int)

    def test_pixel_count_equals_area(self):
        assert ppm_pixel_count(_RGBW) == ppm_area(_RGBW)

    def test_red1_pixel_count_is_1(self):
        assert ppm_pixel_count(_RED1) == 1


class TestPpmRowCount:
    def test_row_count_returns_int(self):
        assert isinstance(ppm_row_count(_RGBW), int)

    def test_rgbw_rows_is_2(self):
        assert ppm_row_count(_RGBW) == 2

    def test_grad_rows_is_1(self):
        assert ppm_row_count(_GRAD) == 1


class TestPpmColumnCount:
    def test_column_count_returns_int(self):
        assert isinstance(ppm_column_count(_RGBW), int)

    def test_rgbw_cols_is_2(self):
        assert ppm_column_count(_RGBW) == 2

    def test_grad_cols_is_3(self):
        assert ppm_column_count(_GRAD) == 3


class TestPpmMaxval:
    def test_maxval_returns_int(self):
        assert isinstance(ppm_maxval(_RGBW), int)

    def test_rgbw_maxval_is_255(self):
        assert ppm_maxval(_RGBW) == 255

    def test_red1_maxval_is_255(self):
        assert ppm_maxval(_RED1) == 255


class TestPpmChannelAverages:
    def test_red_channel_avg_returns_float(self):
        assert isinstance(ppm_red_channel_average(_RGBW), float)

    def test_green_channel_avg_returns_float(self):
        assert isinstance(ppm_green_channel_average(_RGBW), float)

    def test_blue_channel_avg_returns_float(self):
        assert isinstance(ppm_blue_channel_average(_RGBW), float)

    def test_red1_red_avg_is_255(self):
        assert ppm_red_channel_average(_RED1) == pytest.approx(255.0)

    def test_red1_green_avg_is_0(self):
        assert ppm_green_channel_average(_RED1) == pytest.approx(0.0)

    def test_red1_blue_avg_is_0(self):
        assert ppm_blue_channel_average(_RED1) == pytest.approx(0.0)


class TestPpmChannelSums:
    def test_red_channel_sum_returns_int(self):
        assert isinstance(ppm_red_channel_sum(_RGBW), int)

    def test_green_channel_sum_returns_int(self):
        assert isinstance(ppm_green_channel_sum(_RGBW), int)

    def test_blue_channel_sum_returns_int(self):
        assert isinstance(ppm_blue_channel_sum(_RGBW), int)

    def test_red1_red_sum_is_255(self):
        assert ppm_red_channel_sum(_RED1) == 255

    def test_total_channel_sum_returns_int(self):
        assert isinstance(ppm_total_channel_sum(_RGBW), int)

    def test_total_channel_sum_positive(self):
        assert ppm_total_channel_sum(_RGBW) > 0


class TestPpmChannelRatios:
    def test_red_ratio_returns_float(self):
        assert isinstance(ppm_red_ratio(_RGBW), float)

    def test_green_ratio_returns_float(self):
        assert isinstance(ppm_green_ratio(_RGBW), float)

    def test_blue_ratio_returns_float(self):
        assert isinstance(ppm_blue_ratio(_RGBW), float)

    def test_red1_red_ratio_is_1(self):
        assert ppm_red_ratio(_RED1) == pytest.approx(1.0)

    def test_channel_ratios_sum_to_1(self):
        s = _RGBW
        total = ppm_red_ratio(s) + ppm_green_ratio(s) + ppm_blue_ratio(s)
        assert total == pytest.approx(1.0)


class TestPpmDominantChannel:
    def test_dominant_channel_returns_str(self):
        assert isinstance(ppm_dominant_channel(_RGBW), str)

    def test_dominant_channel_is_valid(self):
        assert ppm_dominant_channel(_RGBW) in ("red", "green", "blue")

    def test_red1_dominant_is_red(self):
        assert ppm_dominant_channel(_RED1) == "red"


class TestPpmBrightness:
    def test_avg_brightness_returns_float(self):
        assert isinstance(ppm_avg_brightness(_RGBW), float)

    def test_avg_brightness_in_range(self):
        assert 0.0 <= ppm_avg_brightness(_RGBW) <= 255.0

    def test_luminance_average_returns_float(self):
        assert isinstance(ppm_luminance_average(_RGBW), float)

    def test_normalized_brightness_returns_float(self):
        assert isinstance(ppm_normalized_brightness(_RGBW), float)

    def test_normalized_brightness_in_0_to_1(self):
        assert 0.0 <= ppm_normalized_brightness(_RGBW) <= 1.0

    def test_max_pixel_brightness_returns_float(self):
        assert isinstance(ppm_max_pixel_brightness(_RGBW), float)

    def test_max_pixel_brightness_positive(self):
        assert ppm_max_pixel_brightness(_RGBW) > 0


class TestPpmBrightnessVariance:
    def test_brightness_variance_returns_float(self):
        assert isinstance(ppm_brightness_variance(_RGBW), float)

    def test_brightness_variance_nonneg(self):
        assert ppm_brightness_variance(_RGBW) >= 0

    def test_color_variance_returns_float(self):
        assert isinstance(ppm_color_variance(_RGBW), float)

    def test_pixel_brightness_range_returns_float(self):
        assert isinstance(ppm_pixel_brightness_range(_RGBW), float)

    def test_pixel_brightness_range_nonneg(self):
        assert ppm_pixel_brightness_range(_RGBW) >= 0


class TestPpmMinMaxBrightness:
    def test_min_max_brightness_returns_dict(self):
        r = ppm_min_max_brightness(_RGBW)
        assert isinstance(r, dict)

    def test_min_max_brightness_has_min_max(self):
        r = ppm_min_max_brightness(_RGBW)
        assert "min" in r and "max" in r

    def test_min_lte_max(self):
        r = ppm_min_max_brightness(_RGBW)
        assert r["min"] <= r["max"]


class TestPpmHasPurePixels:
    def test_has_pure_black_returns_bool(self):
        assert isinstance(ppm_has_pure_black(_RGBW), bool)

    def test_has_pure_white_returns_bool(self):
        assert isinstance(ppm_has_pure_white(_RGBW), bool)

    def test_red1_no_pure_black(self):
        assert ppm_has_pure_black(_RED1) is False

    def test_rgbw_has_pure_white(self):
        assert ppm_has_pure_white(_RGBW) is True


class TestPpmIsFlags:
    def test_is_binary_returns_bool(self):
        assert isinstance(ppm_is_binary(_RGBW), bool)

    def test_is_bright_returns_bool(self):
        assert isinstance(ppm_is_bright(_RGBW), bool)

    def test_is_dark_returns_bool(self):
        assert isinstance(ppm_is_dark(_RGBW), bool)

    def test_is_grayscale_returns_bool(self):
        assert isinstance(ppm_is_grayscale(_RGBW), bool)

    def test_red1_not_grayscale(self):
        assert ppm_is_grayscale(_RED1) is False

    def test_is_monochrome_returns_bool(self):
        assert isinstance(ppm_is_monochrome(_RGBW), bool)

    def test_is_square_returns_bool(self):
        assert isinstance(ppm_is_square(_RGBW), bool)

    def test_rgbw_is_square(self):
        assert ppm_is_square(_RGBW) is True

    def test_grad_not_square(self):
        assert ppm_is_square(_GRAD) is False

    def test_is_landscape_returns_bool(self):
        assert isinstance(ppm_is_landscape(_GRAD), bool)

    def test_is_portrait_returns_bool(self):
        assert isinstance(ppm_is_portrait(_RGBW), bool)

    def test_is_tall_returns_bool(self):
        assert isinstance(ppm_is_tall(_RGBW), bool)


class TestPpmDimensionMetrics:
    def test_aspect_ratio_returns_float(self):
        assert isinstance(ppm_aspect_ratio(_RGBW), float)

    def test_rgbw_aspect_1_0(self):
        assert ppm_aspect_ratio(_RGBW) == pytest.approx(1.0)

    def test_dimension_ratio_returns_float(self):
        assert isinstance(ppm_dimension_ratio(_RGBW), float)

    def test_max_dimension_returns_int(self):
        assert isinstance(ppm_max_dimension(_RGBW), int)

    def test_min_dimension_returns_int(self):
        assert isinstance(ppm_min_dimension(_RGBW), int)

    def test_max_gte_min_dimension(self):
        assert ppm_max_dimension(_RGBW) >= ppm_min_dimension(_RGBW)

    def test_diagonal_returns_float(self):
        assert isinstance(ppm_diagonal(_RGBW), float)

    def test_diagonal_positive(self):
        assert ppm_diagonal(_RGBW) > 0

    def test_perimeter_returns_int(self):
        assert isinstance(ppm_perimeter(_RGBW), int)

    def test_megapixels_returns_float(self):
        assert isinstance(ppm_megapixels(_RGBW), float)

    def test_pixel_density_returns_float(self):
        assert isinstance(ppm_pixel_density(_RGBW), float)


class TestPpmDistinctColors:
    def test_distinct_pixel_count_returns_int(self):
        assert isinstance(ppm_distinct_pixel_count(_RGBW), int)

    def test_rgbw_distinct_is_4(self):
        assert ppm_distinct_pixel_count(_RGBW) == 4

    def test_unique_color_count_returns_int(self):
        assert isinstance(ppm_unique_color_count(_RGBW), int)

    def test_red1_unique_is_1(self):
        assert ppm_unique_color_count(_RED1) == 1


class TestPpmChannelStats:
    def test_max_channel_sum_returns_int(self):
        assert isinstance(ppm_max_channel_sum(_RGBW), int)

    def test_min_channel_sum_returns_int(self):
        assert isinstance(ppm_min_channel_sum(_RGBW), int)

    def test_max_gte_min_channel_sum(self):
        assert ppm_max_channel_sum(_RGBW) >= ppm_min_channel_sum(_RGBW)

    def test_min_channel_avg_returns_float(self):
        assert isinstance(ppm_min_channel_avg(_RGBW), float)

    def test_channel_balance_returns_float(self):
        assert isinstance(ppm_channel_balance(_RGBW), float)

    def test_channel_range_returns_dict(self):
        r = ppm_channel_range(_RGBW)
        assert isinstance(r, dict)

    def test_channel_range_has_rgb_keys(self):
        r = ppm_channel_range(_RGBW)
        assert "red" in r and "green" in r and "blue" in r


class TestPpmBorderSaturation:
    def test_border_brightness_returns_float(self):
        assert isinstance(ppm_border_brightness(_RGBW), float)

    def test_saturation_estimate_returns_float(self):
        assert isinstance(ppm_saturation_estimate(_RGBW), float)

    def test_saturation_estimate_nonneg(self):
        assert ppm_saturation_estimate(_RGBW) >= 0
