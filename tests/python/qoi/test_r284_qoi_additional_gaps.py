"""
Tests for additional QOI analytics gap closure (8 FOSS gaps).
Closes: QOI_SATURATI, QOI_PIXEL_CO, QOI_TOTAL_RG, QOI_RED_BLUE,
        QOI_NORMALIZ, QOI_MIN_BRIG, QOI_ABOVE_ME, QOI_IS_WIDE
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi.qoi_parser import (
    qoi_saturation_estimate,
    qoi_pixel_contrast,
    qoi_total_rgb_sum,
    qoi_red_blue_ratio,
    qoi_normalized_brightness,
    qoi_min_brightness,
    qoi_above_mean_ratio,
    qoi_is_wide,
)

_QOI_1x1 = _REPO / "samples/by-format/qoi/valid/1x1-red.qoi"
_QOI_2x2 = _REPO / "samples/by-format/qoi/valid/2x2-black.qoi"
_QOI_4x1 = _REPO / "samples/by-format/qoi/valid/4x1-gradient.qoi"


class TestQoiSaturationEstimate:
    def test_returns_float(self):
        assert isinstance(qoi_saturation_estimate(_QOI_1x1), float)

    def test_pure_red_is_saturated(self):
        # 1x1-red: R=255, G=0, B=0 → max saturation = 1.0
        assert qoi_saturation_estimate(_QOI_1x1) == pytest.approx(1.0)

    def test_black_zero_saturation(self):
        assert qoi_saturation_estimate(_QOI_2x2) == pytest.approx(0.0)

    def test_bounded(self):
        assert 0.0 <= qoi_saturation_estimate(_QOI_4x1) <= 1.0


class TestQoiPixelContrast:
    def test_returns_float(self):
        assert isinstance(qoi_pixel_contrast(_QOI_1x1), float)

    def test_single_color_zero_contrast(self):
        # 1x1: only one pixel → no variation → 0.0
        assert qoi_pixel_contrast(_QOI_1x1) == pytest.approx(0.0)

    def test_gradient_has_contrast(self):
        # 4x1-gradient has varying brightness
        assert qoi_pixel_contrast(_QOI_4x1) > 0.0

    def test_nonnegative(self):
        assert qoi_pixel_contrast(_QOI_2x2) >= 0.0


class TestQoiTotalRgbSum:
    def test_returns_int(self):
        assert isinstance(qoi_total_rgb_sum(_QOI_1x1), int)

    def test_1x1_red_value(self):
        # 1x1-red: R=255, G=0, B=0 → sum=255
        assert qoi_total_rgb_sum(_QOI_1x1) == 255

    def test_black_is_zero(self):
        assert qoi_total_rgb_sum(_QOI_2x2) == 0

    def test_nonnegative(self):
        assert qoi_total_rgb_sum(_QOI_4x1) >= 0


class TestQoiRedBlueRatio:
    def test_returns_float(self):
        assert isinstance(qoi_red_blue_ratio(_QOI_1x1), float)

    def test_gradient_ratio_nonneg(self):
        assert qoi_red_blue_ratio(_QOI_4x1) >= 0.0

    def test_black_ratio_zero(self):
        # All black: R=0, B=0 → ratio = 0
        assert qoi_red_blue_ratio(_QOI_2x2) == pytest.approx(0.0)

    def test_bounded_or_nonneg(self):
        result = qoi_red_blue_ratio(_QOI_1x1)
        assert isinstance(result, float) and result >= 0.0


class TestQoiNormalizedBrightness:
    def test_returns_float(self):
        assert isinstance(qoi_normalized_brightness(_QOI_1x1), float)

    def test_bounded_0_to_1(self):
        assert 0.0 <= qoi_normalized_brightness(_QOI_1x1) <= 1.0

    def test_black_is_zero(self):
        assert qoi_normalized_brightness(_QOI_2x2) == pytest.approx(0.0)

    def test_red_is_one_third(self):
        # 1x1-red: (255+0+0)/3/255 = 1/3
        assert qoi_normalized_brightness(_QOI_1x1) == pytest.approx(1/3, rel=1e-3)


class TestQoiMinBrightness:
    def test_returns_float(self):
        assert isinstance(qoi_min_brightness(_QOI_1x1), float)

    def test_black_is_zero(self):
        assert qoi_min_brightness(_QOI_2x2) == pytest.approx(0.0)

    def test_gradient_min_is_zero(self):
        # 4x1-gradient starts at black
        assert qoi_min_brightness(_QOI_4x1) == pytest.approx(0.0)

    def test_nonnegative(self):
        assert qoi_min_brightness(_QOI_1x1) >= 0.0


class TestQoiAboveMeanRatio:
    def test_returns_float(self):
        assert isinstance(qoi_above_mean_ratio(_QOI_1x1), float)

    def test_black_zero_above_mean(self):
        # All black pixels: none above mean
        assert qoi_above_mean_ratio(_QOI_2x2) == pytest.approx(0.0)

    def test_bounded(self):
        assert 0.0 <= qoi_above_mean_ratio(_QOI_4x1) <= 1.0

    def test_gradient_has_some_above_mean(self):
        # 4x1-gradient: half are above mean
        assert qoi_above_mean_ratio(_QOI_4x1) == pytest.approx(0.5, rel=1e-3)


class TestQoiIsWide:
    def test_returns_bool(self):
        assert isinstance(qoi_is_wide(_QOI_1x1), bool)

    def test_square_not_wide(self):
        assert qoi_is_wide(_QOI_1x1) is False

    def test_4x1_is_wide(self):
        # 4x1 has width=4, height=1 → wide
        assert qoi_is_wide(_QOI_4x1) is True

    def test_2x2_not_wide(self):
        assert qoi_is_wide(_QOI_2x2) is False
