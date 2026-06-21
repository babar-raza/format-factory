"""Tests for PGM analytics functions — coverage sprint r374.

Covers 55 pgm_ analytics functions using 3 real PGM sample files.
Each test asserts return type and plausible value.
"""
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm import (
    pgm_above_mean_ratio, pgm_area, pgm_aspect_ratio, pgm_average_brightness,
    pgm_avg_row_brightness, pgm_bright_pixel_ratio, pgm_brightness_histogram,
    pgm_brightness_quartiles, pgm_brightness_range, pgm_brightness_ratio,
    pgm_column_count, pgm_contrast_range, pgm_contrast_ratio, pgm_dark_pixel_count,
    pgm_dark_pixel_ratio, pgm_diagonal, pgm_dimension_ratio, pgm_dynamic_range,
    pgm_has_any_saturated, pgm_has_any_zero, pgm_is_all_bright, pgm_is_all_dark,
    pgm_is_bright, pgm_is_high_contrast, pgm_is_landscape, pgm_is_portrait,
    pgm_is_square, pgm_is_tall, pgm_is_uniform, pgm_is_wide,
    pgm_max_dimension, pgm_max_pixel_value, pgm_maxval, pgm_mean_brightness,
    pgm_median_brightness, pgm_median_pixel_value, pgm_megapixels, pgm_midpoint_gray,
    pgm_min_brightness, pgm_min_dimension, pgm_min_pixel_value, pgm_nonzero_pixel_ratio,
    pgm_normalized_mean, pgm_perimeter, pgm_pixel_density, pgm_pixel_sum,
    pgm_pixel_value_range, pgm_row_brightness_variance, pgm_row_count,
    pgm_saturated_pixel_count, pgm_saturated_pixel_ratio, pgm_standard_deviation,
    pgm_total_pixel_count, pgm_unique_value_count, pgm_zero_pixel_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "pgm" / "valid"
_GRADIENT = str(_SAMPLES / "2x2-gradient.pgm")  # 2x2, full range 0-85-170-255
_RAMP     = str(_SAMPLES / "3x1-ramp.pgm")      # 3x1 ramp
_WHITE1   = str(_SAMPLES / "1x1-white.pgm")     # 1x1 white (255)


class TestPgmArea:
    def test_area_returns_int(self):
        assert isinstance(pgm_area(_GRADIENT), int)

    def test_gradient_area_is_4(self):
        assert pgm_area(_GRADIENT) == 4

    def test_ramp_area_is_3(self):
        assert pgm_area(_RAMP) == 3

    def test_white1_area_is_1(self):
        assert pgm_area(_WHITE1) == 1


class TestPgmRowCount:
    def test_row_count_returns_int(self):
        assert isinstance(pgm_row_count(_GRADIENT), int)

    def test_gradient_rows_is_2(self):
        assert pgm_row_count(_GRADIENT) == 2

    def test_ramp_rows_is_1(self):
        assert pgm_row_count(_RAMP) == 1


class TestPgmColumnCount:
    def test_column_count_returns_int(self):
        assert isinstance(pgm_column_count(_GRADIENT), int)

    def test_gradient_cols_is_2(self):
        assert pgm_column_count(_GRADIENT) == 2

    def test_ramp_cols_is_3(self):
        assert pgm_column_count(_RAMP) == 3


class TestPgmMaxval:
    def test_maxval_returns_int(self):
        assert isinstance(pgm_maxval(_GRADIENT), int)

    def test_gradient_maxval_is_255(self):
        assert pgm_maxval(_GRADIENT) == 255

    def test_white1_maxval_is_255(self):
        assert pgm_maxval(_WHITE1) == 255

    def test_max_pixel_value_matches_maxval(self):
        assert pgm_max_pixel_value(_GRADIENT) <= pgm_maxval(_GRADIENT)


class TestPgmPixelValues:
    def test_max_pixel_value_returns_int(self):
        assert isinstance(pgm_max_pixel_value(_GRADIENT), int)

    def test_min_pixel_value_returns_int(self):
        assert isinstance(pgm_min_pixel_value(_GRADIENT), int)

    def test_min_lte_max_pixel_value(self):
        assert pgm_min_pixel_value(_GRADIENT) <= pgm_max_pixel_value(_GRADIENT)

    def test_gradient_has_zero_min(self):
        assert pgm_min_pixel_value(_GRADIENT) == 0

    def test_gradient_has_255_max(self):
        assert pgm_max_pixel_value(_GRADIENT) == 255

    def test_median_pixel_value_returns_int(self):
        assert isinstance(pgm_median_pixel_value(_GRADIENT), int)

    def test_pixel_value_range_returns_int(self):
        assert isinstance(pgm_pixel_value_range(_GRADIENT), int)

    def test_pixel_value_range_is_max_minus_min(self):
        assert pgm_pixel_value_range(_GRADIENT) == (
            pgm_max_pixel_value(_GRADIENT) - pgm_min_pixel_value(_GRADIENT)
        )


class TestPgmBrightness:
    def test_mean_brightness_returns_float(self):
        assert isinstance(pgm_mean_brightness(_GRADIENT), float)

    def test_average_brightness_returns_float(self):
        assert isinstance(pgm_average_brightness(_GRADIENT), float)

    def test_mean_equals_average(self):
        assert pgm_mean_brightness(_GRADIENT) == pytest.approx(pgm_average_brightness(_GRADIENT))

    def test_gradient_mean_is_127_5(self):
        assert pgm_mean_brightness(_GRADIENT) == pytest.approx(127.5)

    def test_median_brightness_returns_float(self):
        assert isinstance(pgm_median_brightness(_GRADIENT), float)

    def test_min_brightness_returns_numeric(self):
        r = pgm_min_brightness(_GRADIENT)
        assert isinstance(r, (int, float))

    def test_brightness_range_returns_numeric(self):
        r = pgm_brightness_range(_GRADIENT)
        assert isinstance(r, (int, float))

    def test_gradient_brightness_range_is_255(self):
        assert pgm_brightness_range(_GRADIENT) == pytest.approx(255.0)


class TestPgmPixelSum:
    def test_pixel_sum_returns_int(self):
        assert isinstance(pgm_pixel_sum(_GRADIENT), int)

    def test_gradient_pixel_sum_is_510(self):
        assert pgm_pixel_sum(_GRADIENT) == 510

    def test_white1_pixel_sum_is_255(self):
        assert pgm_pixel_sum(_WHITE1) == 255


class TestPgmDynamicRange:
    def test_dynamic_range_returns_int(self):
        assert isinstance(pgm_dynamic_range(_GRADIENT), int)

    def test_gradient_dynamic_range_is_255(self):
        assert pgm_dynamic_range(_GRADIENT) == 255

    def test_white1_dynamic_range_is_0(self):
        assert pgm_dynamic_range(_WHITE1) == 0

    def test_contrast_range_returns_numeric(self):
        assert isinstance(pgm_contrast_range(_GRADIENT), (int, float))

    def test_contrast_ratio_returns_float(self):
        assert isinstance(pgm_contrast_ratio(_GRADIENT), float)


class TestPgmHasAny:
    def test_has_any_zero_returns_bool(self):
        assert isinstance(pgm_has_any_zero(_GRADIENT), bool)

    def test_gradient_has_zero(self):
        assert pgm_has_any_zero(_GRADIENT) is True

    def test_white1_no_zero(self):
        assert pgm_has_any_zero(_WHITE1) is False

    def test_has_any_saturated_returns_bool(self):
        assert isinstance(pgm_has_any_saturated(_GRADIENT), bool)

    def test_gradient_has_saturated(self):
        assert pgm_has_any_saturated(_GRADIENT) is True


class TestPgmIsAllBrightDark:
    def test_is_all_bright_returns_bool(self):
        assert isinstance(pgm_is_all_bright(_GRADIENT), bool)

    def test_is_all_dark_returns_bool(self):
        assert isinstance(pgm_is_all_dark(_GRADIENT), bool)

    def test_gradient_not_all_bright(self):
        assert pgm_is_all_bright(_GRADIENT) is False

    def test_gradient_not_all_dark(self):
        assert pgm_is_all_dark(_GRADIENT) is False

    def test_white1_is_all_bright(self):
        assert pgm_is_all_bright(_WHITE1) is True


class TestPgmIsBright:
    def test_is_bright_returns_bool(self):
        assert isinstance(pgm_is_bright(_GRADIENT), bool)

    def test_is_uniform_returns_bool(self):
        assert isinstance(pgm_is_uniform(_GRADIENT), bool)

    def test_gradient_not_uniform(self):
        assert pgm_is_uniform(_GRADIENT) is False

    def test_white1_is_uniform(self):
        assert pgm_is_uniform(_WHITE1) is True

    def test_is_high_contrast_returns_bool(self):
        assert isinstance(pgm_is_high_contrast(_GRADIENT), bool)

    def test_gradient_is_high_contrast(self):
        assert pgm_is_high_contrast(_GRADIENT) is True


class TestPgmZeroAndSaturated:
    def test_zero_pixel_count_returns_int(self):
        assert isinstance(pgm_zero_pixel_count(_GRADIENT), int)

    def test_gradient_has_one_zero(self):
        assert pgm_zero_pixel_count(_GRADIENT) == 1

    def test_saturated_pixel_count_returns_int(self):
        assert isinstance(pgm_saturated_pixel_count(_GRADIENT), int)

    def test_saturated_pixel_ratio_returns_float(self):
        assert isinstance(pgm_saturated_pixel_ratio(_GRADIENT), float)

    def test_nonzero_pixel_ratio_returns_float(self):
        assert isinstance(pgm_nonzero_pixel_ratio(_GRADIENT), float)

    def test_nonzero_ratio_in_0_to_1(self):
        assert 0.0 <= pgm_nonzero_pixel_ratio(_GRADIENT) <= 1.0


class TestPgmDarkBright:
    def test_dark_pixel_count_returns_int(self):
        assert isinstance(pgm_dark_pixel_count(_GRADIENT), int)

    def test_dark_pixel_ratio_returns_float(self):
        assert isinstance(pgm_dark_pixel_ratio(_GRADIENT), float)

    def test_dark_ratio_in_0_to_1(self):
        assert 0.0 <= pgm_dark_pixel_ratio(_GRADIENT) <= 1.0

    def test_bright_pixel_ratio_returns_float(self):
        assert isinstance(pgm_bright_pixel_ratio(_GRADIENT), float)

    def test_above_mean_ratio_returns_float(self):
        assert isinstance(pgm_above_mean_ratio(_GRADIENT), float)

    def test_above_mean_ratio_in_0_to_1(self):
        assert 0.0 <= pgm_above_mean_ratio(_GRADIENT) <= 1.0


class TestPgmShapeFlags:
    def test_is_square_returns_bool(self):
        assert isinstance(pgm_is_square(_GRADIENT), bool)

    def test_gradient_is_square(self):
        assert pgm_is_square(_GRADIENT) is True

    def test_ramp_not_square(self):
        assert pgm_is_square(_RAMP) is False

    def test_is_landscape_returns_bool(self):
        assert isinstance(pgm_is_landscape(_RAMP), bool)

    def test_ramp_is_landscape(self):
        assert pgm_is_landscape(_RAMP) is True

    def test_is_portrait_returns_bool(self):
        assert isinstance(pgm_is_portrait(_GRADIENT), bool)

    def test_is_tall_returns_bool(self):
        assert isinstance(pgm_is_tall(_GRADIENT), bool)

    def test_is_wide_returns_bool(self):
        assert isinstance(pgm_is_wide(_GRADIENT), bool)


class TestPgmDimensionMetrics:
    def test_aspect_ratio_returns_float(self):
        assert isinstance(pgm_aspect_ratio(_GRADIENT), float)

    def test_gradient_aspect_1_0(self):
        assert pgm_aspect_ratio(_GRADIENT) == pytest.approx(1.0)

    def test_dimension_ratio_returns_float(self):
        assert isinstance(pgm_dimension_ratio(_GRADIENT), float)

    def test_max_dimension_returns_int(self):
        assert isinstance(pgm_max_dimension(_GRADIENT), int)

    def test_min_dimension_returns_int(self):
        assert isinstance(pgm_min_dimension(_GRADIENT), int)

    def test_max_gte_min_dimension(self):
        assert pgm_max_dimension(_GRADIENT) >= pgm_min_dimension(_GRADIENT)


class TestPgmDiagonalPerimeterMegapixels:
    def test_diagonal_returns_float(self):
        assert isinstance(pgm_diagonal(_GRADIENT), float)

    def test_diagonal_positive(self):
        assert pgm_diagonal(_GRADIENT) > 0

    def test_perimeter_returns_int(self):
        assert isinstance(pgm_perimeter(_GRADIENT), int)

    def test_perimeter_positive(self):
        assert pgm_perimeter(_GRADIENT) > 0

    def test_megapixels_returns_float(self):
        assert isinstance(pgm_megapixels(_GRADIENT), float)

    def test_megapixels_positive(self):
        assert pgm_megapixels(_GRADIENT) > 0

    def test_pixel_density_returns_float(self):
        assert isinstance(pgm_pixel_density(_GRADIENT), float)


class TestPgmNormalizedStats:
    def test_normalized_mean_returns_float(self):
        assert isinstance(pgm_normalized_mean(_GRADIENT), float)

    def test_normalized_mean_in_0_to_1(self):
        assert 0.0 <= pgm_normalized_mean(_GRADIENT) <= 1.0

    def test_gradient_normalized_mean_0_5(self):
        assert pgm_normalized_mean(_GRADIENT) == pytest.approx(0.5)

    def test_brightness_ratio_returns_float(self):
        assert isinstance(pgm_brightness_ratio(_GRADIENT), float)

    def test_standard_deviation_returns_float(self):
        assert isinstance(pgm_standard_deviation(_GRADIENT), float)

    def test_standard_deviation_nonneg(self):
        assert pgm_standard_deviation(_GRADIENT) >= 0

    def test_midpoint_gray_returns_int(self):
        assert isinstance(pgm_midpoint_gray(_GRADIENT), int)


class TestPgmHistogramQuartiles:
    def test_brightness_histogram_returns_list(self):
        assert isinstance(pgm_brightness_histogram(_GRADIENT), list)

    def test_brightness_histogram_nonempty(self):
        assert len(pgm_brightness_histogram(_GRADIENT)) > 0

    def test_brightness_quartiles_returns_dict(self):
        r = pgm_brightness_quartiles(_GRADIENT)
        assert isinstance(r, dict)

    def test_brightness_quartiles_has_q25_q50_q75(self):
        r = pgm_brightness_quartiles(_GRADIENT)
        assert "q25" in r and "q50" in r and "q75" in r


class TestPgmRowBrightness:
    def test_avg_row_brightness_returns_list(self):
        assert isinstance(pgm_avg_row_brightness(_GRADIENT), list)

    def test_avg_row_brightness_length_equals_rows(self):
        r = pgm_avg_row_brightness(_GRADIENT)
        assert len(r) == pgm_row_count(_GRADIENT)

    def test_row_brightness_variance_returns_float(self):
        assert isinstance(pgm_row_brightness_variance(_GRADIENT), float)


class TestPgmTotalPixelCount:
    def test_total_pixel_count_returns_int(self):
        assert isinstance(pgm_total_pixel_count(_GRADIENT), int)

    def test_gradient_total_is_4(self):
        assert pgm_total_pixel_count(_GRADIENT) == 4

    def test_unique_value_count_returns_int(self):
        assert isinstance(pgm_unique_value_count(_GRADIENT), int)

    def test_unique_value_count_positive(self):
        assert pgm_unique_value_count(_GRADIENT) > 0

    def test_unique_lte_total(self):
        assert pgm_unique_value_count(_GRADIENT) <= pgm_total_pixel_count(_GRADIENT)
