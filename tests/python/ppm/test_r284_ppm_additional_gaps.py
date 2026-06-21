"""
Tests for additional PPM analytics gap closure (11 FOSS gaps).
Closes: PPM_RED_RATI, PPM_BORDER_B, PPM_GREEN_RA, PPM_PIXEL_BR,
        PPM_BLUE_RAT, PPM_IS_BRIGH, PPM_MAXVAL, PPM_NORMALIZ,
        PPM_AREA, PPM_MIN_CHAN, PPM_MAX_PIXE
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import (
    ppm_red_ratio,
    ppm_border_brightness,
    ppm_green_ratio,
    ppm_pixel_brightness_range,
    ppm_blue_ratio,
    ppm_is_bright,
    ppm_maxval,
    ppm_normalized_brightness,
    ppm_area,
    ppm_min_channel_avg,
    ppm_max_pixel_brightness,
)

_PPM_1x1 = _REPO / "samples/by-format/ppm/valid/1x1-red.ppm"
_PPM_2x2 = _REPO / "samples/by-format/ppm/valid/2x2-rgbw.ppm"


class TestPpmRedRatio:
    def test_returns_float(self):
        assert isinstance(ppm_red_ratio(_PPM_1x1), float)

    def test_pure_red_returns_one(self):
        assert ppm_red_ratio(_PPM_1x1) == pytest.approx(1.0)

    def test_mixed_less_than_one(self):
        assert ppm_red_ratio(_PPM_2x2) < 1.0

    def test_bounded(self):
        assert 0.0 <= ppm_red_ratio(_PPM_2x2) <= 1.0


class TestPpmBorderBrightness:
    def test_returns_float(self):
        assert isinstance(ppm_border_brightness(_PPM_1x1), float)

    def test_nonnegative(self):
        assert ppm_border_brightness(_PPM_1x1) >= 0.0

    def test_1x1_value(self):
        # 1x1-red: brightness = (255+0+0)/3 = 85.0
        assert ppm_border_brightness(_PPM_1x1) == pytest.approx(85.0)

    def test_2x2_nonnegative(self):
        assert ppm_border_brightness(_PPM_2x2) >= 0.0


class TestPpmGreenRatio:
    def test_returns_float(self):
        assert isinstance(ppm_green_ratio(_PPM_1x1), float)

    def test_pure_red_zero_green(self):
        assert ppm_green_ratio(_PPM_1x1) == pytest.approx(0.0)

    def test_mixed_nonnegative(self):
        assert ppm_green_ratio(_PPM_2x2) >= 0.0

    def test_bounded(self):
        assert 0.0 <= ppm_green_ratio(_PPM_2x2) <= 1.0


class TestPpmPixelBrightnessRange:
    def test_returns_float(self):
        assert isinstance(ppm_pixel_brightness_range(_PPM_1x1), float)

    def test_single_color_pixel_zero_range(self):
        # 1x1 single pixel → no variation → range = 0
        assert ppm_pixel_brightness_range(_PPM_1x1) == pytest.approx(0.0)

    def test_multi_color_positive_range(self):
        assert ppm_pixel_brightness_range(_PPM_2x2) > 0.0

    def test_nonnegative(self):
        assert ppm_pixel_brightness_range(_PPM_2x2) >= 0.0


class TestPpmBlueRatio:
    def test_returns_float(self):
        assert isinstance(ppm_blue_ratio(_PPM_1x1), float)

    def test_pure_red_zero_blue(self):
        assert ppm_blue_ratio(_PPM_1x1) == pytest.approx(0.0)

    def test_mixed_nonnegative(self):
        assert ppm_blue_ratio(_PPM_2x2) >= 0.0

    def test_bounded(self):
        assert 0.0 <= ppm_blue_ratio(_PPM_2x2) <= 1.0


class TestPpmIsBright:
    def test_returns_bool(self):
        assert isinstance(ppm_is_bright(_PPM_1x1), bool)

    def test_returns_bool_2x2(self):
        assert isinstance(ppm_is_bright(_PPM_2x2), bool)

    def test_1x1_red_not_bright(self):
        # 1x1-red: avg=(255+0+0)/3=85 < 128 threshold → not bright
        assert ppm_is_bright(_PPM_1x1) is False

    def test_consistent_type(self):
        result = ppm_is_bright(_PPM_2x2)
        assert result is True or result is False


class TestPpmMaxval:
    def test_returns_int(self):
        assert isinstance(ppm_maxval(_PPM_1x1), int)

    def test_1x1_maxval_255(self):
        assert ppm_maxval(_PPM_1x1) == 255

    def test_2x2_maxval_255(self):
        assert ppm_maxval(_PPM_2x2) == 255

    def test_positive(self):
        assert ppm_maxval(_PPM_1x1) > 0


class TestPpmNormalizedBrightness:
    def test_returns_float(self):
        assert isinstance(ppm_normalized_brightness(_PPM_1x1), float)

    def test_bounded_0_to_1(self):
        assert 0.0 <= ppm_normalized_brightness(_PPM_1x1) <= 1.0

    def test_1x1_red_value(self):
        # 1x1-red: avg=85/255 ≈ 0.333
        assert ppm_normalized_brightness(_PPM_1x1) == pytest.approx(1/3, rel=1e-3)

    def test_2x2_value(self):
        assert ppm_normalized_brightness(_PPM_2x2) == pytest.approx(0.5, rel=1e-3)


class TestPpmArea:
    def test_returns_int(self):
        assert isinstance(ppm_area(_PPM_1x1), int)

    def test_1x1_area_is_1(self):
        assert ppm_area(_PPM_1x1) == 1

    def test_2x2_area_is_4(self):
        assert ppm_area(_PPM_2x2) == 4

    def test_positive(self):
        assert ppm_area(_PPM_1x1) > 0


class TestPpmMinChannelAvg:
    def test_returns_float(self):
        assert isinstance(ppm_min_channel_avg(_PPM_1x1), float)

    def test_1x1_red_min_is_zero(self):
        # 1x1-red: R=255, G=0, B=0 → min channel avg = 0.0
        assert ppm_min_channel_avg(_PPM_1x1) == pytest.approx(0.0)

    def test_nonnegative(self):
        assert ppm_min_channel_avg(_PPM_2x2) >= 0.0

    def test_2x2_value(self):
        assert ppm_min_channel_avg(_PPM_2x2) == pytest.approx(127.5, rel=1e-3)


class TestPpmMaxPixelBrightness:
    def test_returns_float(self):
        assert isinstance(ppm_max_pixel_brightness(_PPM_1x1), float)

    def test_1x1_red_value(self):
        # 1x1-red: brightness = (255+0+0)/3 = 85.0
        assert ppm_max_pixel_brightness(_PPM_1x1) == pytest.approx(85.0)

    def test_2x2_max_is_255(self):
        assert ppm_max_pixel_brightness(_PPM_2x2) == pytest.approx(255.0)

    def test_positive(self):
        assert ppm_max_pixel_brightness(_PPM_1x1) > 0.0
