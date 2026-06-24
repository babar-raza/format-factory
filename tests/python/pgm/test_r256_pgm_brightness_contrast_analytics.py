"""Tests for PGM gap closure (Sprint 40).

Closes:
  GAP-PGM-FOSS-PGM_IS_HIGH_-001   (Pgm Is High Contrast)
  GAP-PGM-FOSS-PGM_AVG_ROW_-001   (Pgm Avg Row Brightness)
  GAP-PGM-FOSS-PGM_IS_BRIGH-001   (Pgm Is Bright)
  GAP-PGM-FOSS-PGM_DARK_PIX-001   (Pgm Dark Pixel Ratio)
  GAP-PGM-FOSS-PGM_ROW_BRIG-001   (Pgm Row Brightness Variance)
  GAP-PGM-FOSS-PGM_CONTRAST-001   (Pgm Contrast Ratio)
  GAP-PGM-FOSS-PGM_NORMALIZ-001   (Pgm Normalized Mean)
  GAP-PGM-FOSS-PGM_ABOVE_ME-001   (Pgm Above Mean Ratio)
  GAP-PGM-FOSS-PGM_MAXVAL-001     (Pgm Maxval)
  GAP-PGM-FOSS-PGM_MIDPOINT-001   (Pgm Midpoint Gray)
  GAP-PGM-FOSS-PGM_MEDIAN_B-001   (Pgm Median Brightness)
  GAP-PGM-FOSS-PGM_PIXEL_VA-001   (Pgm Pixel Value Range)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import (
    pgm_above_mean_ratio,
    pgm_avg_row_brightness,
    pgm_contrast_ratio,
    pgm_dark_pixel_ratio,
    pgm_is_bright,
    pgm_is_high_contrast,
    pgm_maxval,
    pgm_median_brightness,
    pgm_midpoint_gray,
    pgm_normalized_mean,
    pgm_pixel_value_range,
    pgm_row_brightness_variance,
)

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_1X1_WHITE = str(_DIR / "1x1-white.pgm")
_2X2_GRAD = str(_DIR / "2x2-gradient.pgm")
_3X1_RAMP = str(_DIR / "3x1-ramp.pgm")


class TestPgmIsHighContrast:
    def test_return_type(self):
        assert isinstance(pgm_is_high_contrast(_1X1_WHITE), bool)

    def test_false_for_1x1_white(self):
        # single uniform pixel -> not high contrast
        assert pgm_is_high_contrast(_1X1_WHITE) is False

    def test_true_for_2x2_gradient(self):
        # gradient has 0 and 255 values -> high contrast
        assert pgm_is_high_contrast(_2X2_GRAD) is True

    def test_true_for_3x1_ramp(self):
        assert pgm_is_high_contrast(_3X1_RAMP) is True

    def test_consistent_across_calls(self):
        assert pgm_is_high_contrast(_1X1_WHITE) == pgm_is_high_contrast(_1X1_WHITE)


class TestPgmAvgRowBrightness:
    def test_return_type(self):
        result = pgm_avg_row_brightness(_1X1_WHITE)
        assert isinstance(result, list)

    def test_exact_for_1x1_white(self):
        # single pixel value=255 -> one row with brightness 255.0
        result = pgm_avg_row_brightness(_1X1_WHITE)
        assert result == [255.0]

    def test_two_rows_for_2x2_gradient(self):
        result = pgm_avg_row_brightness(_2X2_GRAD)
        assert len(result) == 2
        assert result[0] == 42.5
        assert result[1] == 212.5

    def test_consistent_across_calls(self):
        assert pgm_avg_row_brightness(_1X1_WHITE) == pgm_avg_row_brightness(_1X1_WHITE)


class TestPgmIsBright:
    def test_return_type(self):
        assert isinstance(pgm_is_bright(_1X1_WHITE), bool)

    def test_true_for_1x1_white(self):
        # value=255 is fully bright
        assert pgm_is_bright(_1X1_WHITE) is True

    def test_false_for_2x2_gradient(self):
        # mixed dark/bright pixels
        assert pgm_is_bright(_2X2_GRAD) is False

    def test_consistent_across_calls(self):
        assert pgm_is_bright(_1X1_WHITE) == pgm_is_bright(_1X1_WHITE)


class TestPgmDarkPixelRatio:
    def test_return_type(self):
        assert isinstance(pgm_dark_pixel_ratio(_1X1_WHITE), float)

    def test_zero_for_1x1_white(self):
        assert pgm_dark_pixel_ratio(_1X1_WHITE) == 0.0

    def test_exact_0_5_for_2x2_gradient(self):
        # threshold=maxval*0.5=127.5; pixels 0,85 are dark -> 2/4 = 0.5
        assert pgm_dark_pixel_ratio(_2X2_GRAD) == 0.5

    def test_between_0_and_1(self):
        ratio = pgm_dark_pixel_ratio(_1X1_WHITE)
        assert 0.0 <= ratio <= 1.0

    def test_consistent_across_calls(self):
        assert pgm_dark_pixel_ratio(_1X1_WHITE) == pgm_dark_pixel_ratio(_1X1_WHITE)


class TestPgmRowBrightnessVariance:
    def test_return_type(self):
        assert isinstance(pgm_row_brightness_variance(_1X1_WHITE), float)

    def test_zero_for_1x1_white(self):
        # single row -> variance = 0
        assert pgm_row_brightness_variance(_1X1_WHITE) == 0.0

    def test_exact_7225_for_2x2_gradient(self):
        assert pgm_row_brightness_variance(_2X2_GRAD) == 7225.0

    def test_nonnegative(self):
        assert pgm_row_brightness_variance(_1X1_WHITE) >= 0.0

    def test_consistent_across_calls(self):
        assert pgm_row_brightness_variance(_2X2_GRAD) == pgm_row_brightness_variance(_2X2_GRAD)


class TestPgmContrastRatio:
    def test_return_type(self):
        assert isinstance(pgm_contrast_ratio(_1X1_WHITE), float)

    def test_zero_for_1x1_white(self):
        # single pixel -> no contrast
        assert pgm_contrast_ratio(_1X1_WHITE) == 0.0

    def test_exact_1_0_for_2x2_gradient(self):
        assert pgm_contrast_ratio(_2X2_GRAD) == 1.0

    def test_between_0_and_1(self):
        ratio = pgm_contrast_ratio(_1X1_WHITE)
        assert 0.0 <= ratio <= 1.0

    def test_consistent_across_calls(self):
        assert pgm_contrast_ratio(_2X2_GRAD) == pgm_contrast_ratio(_2X2_GRAD)


class TestPgmNormalizedMean:
    def test_return_type(self):
        assert isinstance(pgm_normalized_mean(_1X1_WHITE), float)

    def test_exact_1_0_for_1x1_white(self):
        # 255/255 = 1.0
        assert pgm_normalized_mean(_1X1_WHITE) == 1.0

    def test_exact_0_5_for_2x2_gradient(self):
        assert pgm_normalized_mean(_2X2_GRAD) == 0.5

    def test_between_0_and_1(self):
        v = pgm_normalized_mean(_1X1_WHITE)
        assert 0.0 <= v <= 1.0

    def test_consistent_across_calls(self):
        assert pgm_normalized_mean(_1X1_WHITE) == pgm_normalized_mean(_1X1_WHITE)


class TestPgmAboveMeanRatio:
    def test_return_type(self):
        assert isinstance(pgm_above_mean_ratio(_1X1_WHITE), float)

    def test_zero_for_1x1_white(self):
        # single pixel: no pixel above mean (itself is the mean)
        assert pgm_above_mean_ratio(_1X1_WHITE) == 0.0

    def test_exact_0_5_for_2x2_gradient(self):
        assert pgm_above_mean_ratio(_2X2_GRAD) == 0.5

    def test_between_0_and_1(self):
        ratio = pgm_above_mean_ratio(_2X2_GRAD)
        assert 0.0 <= ratio <= 1.0

    def test_consistent_across_calls(self):
        assert pgm_above_mean_ratio(_2X2_GRAD) == pgm_above_mean_ratio(_2X2_GRAD)


class TestPgmMaxval:
    def test_return_type(self):
        assert isinstance(pgm_maxval(_1X1_WHITE), int)

    def test_exact_255_for_1x1_white(self):
        assert pgm_maxval(_1X1_WHITE) == 255

    def test_exact_255_for_2x2_gradient(self):
        assert pgm_maxval(_2X2_GRAD) == 255

    def test_exact_255_for_3x1_ramp(self):
        assert pgm_maxval(_3X1_RAMP) == 255

    def test_positive(self):
        assert pgm_maxval(_1X1_WHITE) >= 1

    def test_consistent_across_calls(self):
        assert pgm_maxval(_1X1_WHITE) == pgm_maxval(_1X1_WHITE)


class TestPgmMidpointGray:
    def test_return_type(self):
        assert isinstance(pgm_midpoint_gray(_1X1_WHITE), int)

    def test_exact_127_for_maxval_255(self):
        # midpoint of 0-255 = 127
        assert pgm_midpoint_gray(_1X1_WHITE) == 127

    def test_exact_127_for_2x2_gradient(self):
        assert pgm_midpoint_gray(_2X2_GRAD) == 127

    def test_nonnegative(self):
        assert pgm_midpoint_gray(_1X1_WHITE) >= 0

    def test_consistent_across_calls(self):
        assert pgm_midpoint_gray(_1X1_WHITE) == pgm_midpoint_gray(_1X1_WHITE)


class TestPgmMedianBrightness:
    def test_return_type(self):
        assert isinstance(pgm_median_brightness(_1X1_WHITE), float)

    def test_exact_255_for_1x1_white(self):
        assert pgm_median_brightness(_1X1_WHITE) == 255.0

    def test_exact_127_5_for_2x2_gradient(self):
        assert pgm_median_brightness(_2X2_GRAD) == 127.5

    def test_nonnegative(self):
        assert pgm_median_brightness(_1X1_WHITE) >= 0.0

    def test_consistent_across_calls(self):
        assert pgm_median_brightness(_1X1_WHITE) == pgm_median_brightness(_1X1_WHITE)


class TestPgmPixelValueRange:
    def test_return_type(self):
        assert isinstance(pgm_pixel_value_range(_1X1_WHITE), int)

    def test_zero_for_1x1_white(self):
        # single pixel value -> range = 0
        assert pgm_pixel_value_range(_1X1_WHITE) == 0

    def test_exact_255_for_2x2_gradient(self):
        # min=0, max=255 -> range = 255
        assert pgm_pixel_value_range(_2X2_GRAD) == 255

    def test_exact_255_for_3x1_ramp(self):
        assert pgm_pixel_value_range(_3X1_RAMP) == 255

    def test_nonnegative(self):
        assert pgm_pixel_value_range(_1X1_WHITE) >= 0

    def test_consistent_across_calls(self):
        assert pgm_pixel_value_range(_2X2_GRAD) == pgm_pixel_value_range(_2X2_GRAD)
