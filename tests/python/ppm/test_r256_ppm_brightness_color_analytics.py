"""Tests for PPM gap closure (Sprint 40).

Closes:
  GAP-PPM-FOSS-PPM_IS_MONOC-001   (Ppm Is Monochrome)
  GAP-PPM-FOSS-PPM_TOTAL_CH-001   (Ppm Total Channel Sum)
  GAP-PPM-FOSS-PPM_AVG_BRIG-001   (Ppm Avg Brightness)
  GAP-PPM-FOSS-PPM_COLOR_VA-001   (Ppm Color Variance)
  GAP-PPM-FOSS-PPM_RED_RATI-001   (Ppm Red Ratio)
  GAP-PPM-FOSS-PPM_BORDER_B-001   (Ppm Border Brightness)
  GAP-PPM-FOSS-PPM_GREEN_RA-001   (Ppm Green Ratio)
  GAP-PPM-FOSS-PPM_PIXEL_BR-001   (Ppm Pixel Brightness Range)
  GAP-PPM-FOSS-PPM_BLUE_RAT-001   (Ppm Blue Ratio)
  GAP-PPM-FOSS-PPM_IS_BRIGH-001   (Ppm Is Bright)
  GAP-PPM-FOSS-PPM_MAXVAL-001     (Ppm Maxval)
  GAP-PPM-FOSS-PPM_NORMALIZ-001   (Ppm Normalized Brightness)
  GAP-PPM-FOSS-PPM_AREA-001       (Ppm Area)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import (
    ppm_area,
    ppm_avg_brightness,
    ppm_blue_ratio,
    ppm_border_brightness,
    ppm_color_variance,
    ppm_green_ratio,
    ppm_is_bright,
    ppm_is_monochrome,
    ppm_maxval,
    ppm_normalized_brightness,
    ppm_pixel_brightness_range,
    ppm_red_ratio,
    ppm_total_channel_sum,
)

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_1X1_RED = str(_DIR / "1x1-red.ppm")
_2X2_RGBW = str(_DIR / "2x2-rgbw.ppm")
_3X1_GRAD = str(_DIR / "3x1-gradient.ppm")


class TestPpmIsMonochrome:
    def test_return_type(self):
        assert isinstance(ppm_is_monochrome(_1X1_RED), bool)

    def test_true_for_1x1_red(self):
        # single color -> monochrome
        assert ppm_is_monochrome(_1X1_RED) is True

    def test_false_for_2x2_rgbw(self):
        # multiple distinct colors
        assert ppm_is_monochrome(_2X2_RGBW) is False

    def test_consistent_across_calls(self):
        assert ppm_is_monochrome(_1X1_RED) == ppm_is_monochrome(_1X1_RED)


class TestPpmTotalChannelSum:
    def test_return_type(self):
        assert isinstance(ppm_total_channel_sum(_1X1_RED), int)

    def test_exact_255_for_1x1_red(self):
        # R=255, G=0, B=0 -> sum=255
        assert ppm_total_channel_sum(_1X1_RED) == 255

    def test_exact_1530_for_2x2_rgbw(self):
        # R(255)+G(255)+B(255)+W(765) = 1530
        assert ppm_total_channel_sum(_2X2_RGBW) == 1530

    def test_nonnegative(self):
        assert ppm_total_channel_sum(_1X1_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_total_channel_sum(_1X1_RED) == ppm_total_channel_sum(_1X1_RED)


class TestPpmAvgBrightness:
    def test_return_type(self):
        assert isinstance(ppm_avg_brightness(_1X1_RED), float)

    def test_exact_85_for_1x1_red(self):
        # (255+0+0)/3 = 85.0
        assert ppm_avg_brightness(_1X1_RED) == 85.0

    def test_positive(self):
        assert ppm_avg_brightness(_1X1_RED) > 0

    def test_between_0_and_255(self):
        b = ppm_avg_brightness(_1X1_RED)
        assert 0.0 <= b <= 255.0

    def test_consistent_across_calls(self):
        assert ppm_avg_brightness(_1X1_RED) == ppm_avg_brightness(_1X1_RED)


class TestPpmColorVariance:
    def test_return_type(self):
        assert isinstance(ppm_color_variance(_1X1_RED), float)

    def test_zero_for_1x1_red(self):
        # single pixel -> no variance
        assert ppm_color_variance(_1X1_RED) == 0.0

    def test_nonzero_for_2x2_rgbw(self):
        assert ppm_color_variance(_2X2_RGBW) > 0

    def test_nonnegative(self):
        assert ppm_color_variance(_1X1_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert ppm_color_variance(_2X2_RGBW) == ppm_color_variance(_2X2_RGBW)


class TestPpmRedRatio:
    def test_return_type(self):
        assert isinstance(ppm_red_ratio(_1X1_RED), float)

    def test_exact_1_0_for_1x1_red(self):
        # pure red: all channel sum from red
        assert ppm_red_ratio(_1X1_RED) == 1.0

    def test_nonzero_for_2x2_rgbw(self):
        assert ppm_red_ratio(_2X2_RGBW) > 0

    def test_between_0_and_1(self):
        ratio = ppm_red_ratio(_1X1_RED)
        assert 0.0 <= ratio <= 1.0

    def test_consistent_across_calls(self):
        assert ppm_red_ratio(_1X1_RED) == ppm_red_ratio(_1X1_RED)


class TestPpmBorderBrightness:
    def test_return_type(self):
        assert isinstance(ppm_border_brightness(_1X1_RED), float)

    def test_exact_85_for_1x1_red(self):
        # single pixel is border -> brightness = 85.0
        assert ppm_border_brightness(_1X1_RED) == 85.0

    def test_nonnegative(self):
        assert ppm_border_brightness(_1X1_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert ppm_border_brightness(_1X1_RED) == ppm_border_brightness(_1X1_RED)


class TestPpmGreenRatio:
    def test_return_type(self):
        assert isinstance(ppm_green_ratio(_1X1_RED), float)

    def test_zero_for_1x1_red(self):
        # pure red -> no green
        assert ppm_green_ratio(_1X1_RED) == 0.0

    def test_nonzero_for_2x2_rgbw(self):
        assert ppm_green_ratio(_2X2_RGBW) > 0

    def test_between_0_and_1(self):
        ratio = ppm_green_ratio(_2X2_RGBW)
        assert 0.0 <= ratio <= 1.0

    def test_consistent_across_calls(self):
        assert ppm_green_ratio(_1X1_RED) == ppm_green_ratio(_1X1_RED)


class TestPpmPixelBrightnessRange:
    def test_return_type(self):
        assert isinstance(ppm_pixel_brightness_range(_1X1_RED), float)

    def test_zero_for_1x1_red(self):
        # single pixel -> no range
        assert ppm_pixel_brightness_range(_1X1_RED) == 0.0

    def test_nonzero_for_3x1_gradient(self):
        # gradient has varying brightness
        assert ppm_pixel_brightness_range(_3X1_GRAD) > 0

    def test_nonnegative(self):
        assert ppm_pixel_brightness_range(_1X1_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert ppm_pixel_brightness_range(_3X1_GRAD) == ppm_pixel_brightness_range(_3X1_GRAD)


class TestPpmBlueRatio:
    def test_return_type(self):
        assert isinstance(ppm_blue_ratio(_1X1_RED), float)

    def test_zero_for_1x1_red(self):
        assert ppm_blue_ratio(_1X1_RED) == 0.0

    def test_nonzero_for_2x2_rgbw(self):
        assert ppm_blue_ratio(_2X2_RGBW) > 0

    def test_between_0_and_1(self):
        ratio = ppm_blue_ratio(_2X2_RGBW)
        assert 0.0 <= ratio <= 1.0

    def test_consistent_across_calls(self):
        assert ppm_blue_ratio(_1X1_RED) == ppm_blue_ratio(_1X1_RED)


class TestPpmIsBright:
    def test_return_type(self):
        assert isinstance(ppm_is_bright(_1X1_RED), bool)

    def test_false_for_1x1_red(self):
        # avg brightness = 85 < threshold
        assert ppm_is_bright(_1X1_RED) is False

    def test_false_for_2x2_rgbw(self):
        assert ppm_is_bright(_2X2_RGBW) is False

    def test_consistent_across_calls(self):
        assert ppm_is_bright(_1X1_RED) == ppm_is_bright(_1X1_RED)


class TestPpmMaxval:
    def test_return_type(self):
        assert isinstance(ppm_maxval(_1X1_RED), int)

    def test_exact_255_for_1x1_red(self):
        assert ppm_maxval(_1X1_RED) == 255

    def test_exact_255_for_2x2_rgbw(self):
        assert ppm_maxval(_2X2_RGBW) == 255

    def test_positive(self):
        assert ppm_maxval(_1X1_RED) >= 1

    def test_consistent_across_calls(self):
        assert ppm_maxval(_1X1_RED) == ppm_maxval(_1X1_RED)


class TestPpmNormalizedBrightness:
    def test_return_type(self):
        assert isinstance(ppm_normalized_brightness(_1X1_RED), float)

    def test_between_0_and_1(self):
        v = ppm_normalized_brightness(_1X1_RED)
        assert 0.0 <= v <= 1.0

    def test_nonzero_for_1x1_red(self):
        assert ppm_normalized_brightness(_1X1_RED) > 0

    def test_consistent_across_calls(self):
        assert ppm_normalized_brightness(_1X1_RED) == ppm_normalized_brightness(_1X1_RED)


class TestPpmArea:
    def test_return_type(self):
        assert isinstance(ppm_area(_1X1_RED), int)

    def test_exact_1_for_1x1_red(self):
        assert ppm_area(_1X1_RED) == 1

    def test_exact_4_for_2x2_rgbw(self):
        assert ppm_area(_2X2_RGBW) == 4

    def test_exact_3_for_3x1_gradient(self):
        assert ppm_area(_3X1_GRAD) == 3

    def test_positive(self):
        assert ppm_area(_1X1_RED) >= 1

    def test_consistent_across_calls(self):
        assert ppm_area(_1X1_RED) == ppm_area(_1X1_RED)
