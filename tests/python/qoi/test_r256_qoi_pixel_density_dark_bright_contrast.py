"""Tests for QOI gap closure (Sprint 40).

Closes:
  GAP-QOI-FOSS-QOI_PIXEL_DE-001   (Qoi Pixel Density)
  GAP-QOI-FOSS-QOI_IS_DARK-001    (Qoi Is Dark)
  GAP-QOI-FOSS-QOI_COLOR_DE-001   (Qoi Color Depth Estimate)
  GAP-QOI-FOSS-QOI_IS_BRIGH-001   (Qoi Is Bright)
  GAP-QOI-FOSS-QOI_SATURATI-001   (Qoi Saturation Estimate)
  GAP-QOI-FOSS-QOI_PIXEL_CO-001   (Qoi Pixel Contrast)
  GAP-QOI-FOSS-QOI_TOTAL_RG-001   (Qoi Total Rgb Sum)
  GAP-QOI-FOSS-QOI_RED_BLUE-001   (Qoi Red Blue Ratio)
  GAP-QOI-FOSS-QOI_NORMALIZ-001   (Qoi Normalized Brightness)
  GAP-QOI-FOSS-QOI_MIN_BRIG-001   (Qoi Min Brightness)
  GAP-QOI-FOSS-QOI_ABOVE_ME-001   (Qoi Above Mean Ratio)
  GAP-QOI-FOSS-QOI_IS_WIDE-001    (Qoi Is Wide)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import (
    qoi_above_mean_ratio,
    qoi_color_depth_estimate,
    qoi_is_bright,
    qoi_is_dark,
    qoi_is_wide,
    qoi_min_brightness,
    qoi_normalized_brightness,
    qoi_pixel_contrast,
    qoi_pixel_density,
    qoi_red_blue_ratio,
    qoi_saturation_estimate,
    qoi_total_rgb_sum,
)

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_1X1_RED = str(_DIR / "1x1-red.qoi")
_2X2_BLACK = str(_DIR / "2x2-black.qoi")
_4X1_GRAD = str(_DIR / "4x1-gradient.qoi")


class TestQoiPixelDensity:
    def test_return_type(self):
        assert isinstance(qoi_pixel_density(_1X1_RED), float)

    def test_positive_for_1x1_red(self):
        assert qoi_pixel_density(_1X1_RED) > 0

    def test_positive_for_2x2_black(self):
        assert qoi_pixel_density(_2X2_BLACK) > 0

    def test_between_0_and_1(self):
        d = qoi_pixel_density(_1X1_RED)
        assert 0.0 <= d <= 1.0

    def test_consistent_across_calls(self):
        assert qoi_pixel_density(_1X1_RED) == qoi_pixel_density(_1X1_RED)


class TestQoiIsDark:
    def test_return_type(self):
        assert isinstance(qoi_is_dark(_1X1_RED), bool)

    def test_true_for_1x1_red(self):
        # red pixel has avg brightness 85 < threshold
        assert qoi_is_dark(_1X1_RED) is True

    def test_true_for_2x2_black(self):
        assert qoi_is_dark(_2X2_BLACK) is True

    def test_consistent_across_calls(self):
        assert qoi_is_dark(_1X1_RED) == qoi_is_dark(_1X1_RED)


class TestQoiColorDepthEstimate:
    def test_return_type(self):
        assert isinstance(qoi_color_depth_estimate(_1X1_RED), float)

    def test_zero_for_1x1_red(self):
        # single pixel -> no depth variety
        assert qoi_color_depth_estimate(_1X1_RED) == 0.0

    def test_zero_for_2x2_black(self):
        assert qoi_color_depth_estimate(_2X2_BLACK) == 0.0

    def test_nonzero_for_gradient(self):
        assert qoi_color_depth_estimate(_4X1_GRAD) == 2.0

    def test_nonnegative(self):
        assert qoi_color_depth_estimate(_1X1_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_color_depth_estimate(_4X1_GRAD) == qoi_color_depth_estimate(_4X1_GRAD)


class TestQoiIsBright:
    def test_return_type(self):
        assert isinstance(qoi_is_bright(_1X1_RED), bool)

    def test_false_for_1x1_red(self):
        assert qoi_is_bright(_1X1_RED) is False

    def test_false_for_2x2_black(self):
        assert qoi_is_bright(_2X2_BLACK) is False

    def test_consistent_across_calls(self):
        assert qoi_is_bright(_1X1_RED) == qoi_is_bright(_1X1_RED)


class TestQoiSaturationEstimate:
    def test_return_type(self):
        assert isinstance(qoi_saturation_estimate(_1X1_RED), float)

    def test_exact_1_0_for_1x1_red(self):
        # pure red is fully saturated
        assert qoi_saturation_estimate(_1X1_RED) == 1.0

    def test_zero_for_2x2_black(self):
        # pure black has no saturation
        assert qoi_saturation_estimate(_2X2_BLACK) == 0.0

    def test_between_0_and_1(self):
        s = qoi_saturation_estimate(_1X1_RED)
        assert 0.0 <= s <= 1.0

    def test_consistent_across_calls(self):
        assert qoi_saturation_estimate(_1X1_RED) == qoi_saturation_estimate(_1X1_RED)


class TestQoiPixelContrast:
    def test_return_type(self):
        assert isinstance(qoi_pixel_contrast(_1X1_RED), float)

    def test_zero_for_1x1_red(self):
        # single pixel -> no contrast
        assert qoi_pixel_contrast(_1X1_RED) == 0.0

    def test_zero_for_2x2_black(self):
        assert qoi_pixel_contrast(_2X2_BLACK) == 0.0

    def test_exact_1_0_for_gradient(self):
        assert qoi_pixel_contrast(_4X1_GRAD) == 1.0

    def test_between_0_and_1(self):
        c = qoi_pixel_contrast(_1X1_RED)
        assert 0.0 <= c <= 1.0

    def test_consistent_across_calls(self):
        assert qoi_pixel_contrast(_4X1_GRAD) == qoi_pixel_contrast(_4X1_GRAD)


class TestQoiTotalRgbSum:
    def test_return_type(self):
        assert isinstance(qoi_total_rgb_sum(_1X1_RED), int)

    def test_exact_255_for_1x1_red(self):
        assert qoi_total_rgb_sum(_1X1_RED) == 255

    def test_zero_for_2x2_black(self):
        assert qoi_total_rgb_sum(_2X2_BLACK) == 0

    def test_exact_1530_for_gradient(self):
        assert qoi_total_rgb_sum(_4X1_GRAD) == 1530

    def test_nonnegative(self):
        assert qoi_total_rgb_sum(_1X1_RED) >= 0

    def test_consistent_across_calls(self):
        assert qoi_total_rgb_sum(_4X1_GRAD) == qoi_total_rgb_sum(_4X1_GRAD)


class TestQoiRedBlueRatio:
    def test_return_type(self):
        assert isinstance(qoi_red_blue_ratio(_1X1_RED), float)

    def test_zero_for_2x2_black(self):
        # black has no red or blue
        assert qoi_red_blue_ratio(_2X2_BLACK) == 0.0

    def test_exact_1_0_for_gradient(self):
        assert qoi_red_blue_ratio(_4X1_GRAD) == 1.0

    def test_nonnegative(self):
        assert qoi_red_blue_ratio(_2X2_BLACK) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_red_blue_ratio(_4X1_GRAD) == qoi_red_blue_ratio(_4X1_GRAD)


class TestQoiNormalizedBrightness:
    def test_return_type(self):
        assert isinstance(qoi_normalized_brightness(_1X1_RED), float)

    def test_between_0_and_1(self):
        v = qoi_normalized_brightness(_1X1_RED)
        assert 0.0 <= v <= 1.0

    def test_zero_for_black(self):
        assert qoi_normalized_brightness(_2X2_BLACK) == 0.0

    def test_nonzero_for_1x1_red(self):
        assert qoi_normalized_brightness(_1X1_RED) > 0

    def test_consistent_across_calls(self):
        assert qoi_normalized_brightness(_1X1_RED) == qoi_normalized_brightness(_1X1_RED)


class TestQoiMinBrightness:
    def test_return_type(self):
        assert isinstance(qoi_min_brightness(_1X1_RED), float)

    def test_zero_for_2x2_black(self):
        assert qoi_min_brightness(_2X2_BLACK) == 0.0

    def test_zero_for_gradient(self):
        # gradient starts at black
        assert qoi_min_brightness(_4X1_GRAD) == 0.0

    def test_nonnegative(self):
        assert qoi_min_brightness(_1X1_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_min_brightness(_1X1_RED) == qoi_min_brightness(_1X1_RED)


class TestQoiAboveMeanRatio:
    def test_return_type(self):
        assert isinstance(qoi_above_mean_ratio(_1X1_RED), float)

    def test_zero_for_1x1_red(self):
        # single pixel: not above its own mean
        assert qoi_above_mean_ratio(_1X1_RED) == 0.0

    def test_zero_for_2x2_black(self):
        assert qoi_above_mean_ratio(_2X2_BLACK) == 0.0

    def test_exact_0_5_for_gradient(self):
        assert qoi_above_mean_ratio(_4X1_GRAD) == 0.5

    def test_between_0_and_1(self):
        ratio = qoi_above_mean_ratio(_4X1_GRAD)
        assert 0.0 <= ratio <= 1.0

    def test_consistent_across_calls(self):
        assert qoi_above_mean_ratio(_4X1_GRAD) == qoi_above_mean_ratio(_4X1_GRAD)


class TestQoiIsWide:
    def test_return_type(self):
        assert isinstance(qoi_is_wide(_1X1_RED), bool)

    def test_false_for_1x1_red(self):
        # 1x1 square -> not wide
        assert qoi_is_wide(_1X1_RED) is False

    def test_false_for_2x2_black(self):
        assert qoi_is_wide(_2X2_BLACK) is False

    def test_true_for_4x1_gradient(self):
        # 4 wide x 1 high -> wide
        assert qoi_is_wide(_4X1_GRAD) is True

    def test_consistent_across_calls(self):
        assert qoi_is_wide(_1X1_RED) == qoi_is_wide(_1X1_RED)
