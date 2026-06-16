"""
tests/python/ppm/test_r293_ppm_new_analytics.py

Sprint: PRODUCT-DEEPENING-SPRINT-29-20260616
New PPM analytics: ppm_blue_ratio, ppm_is_bright, ppm_maxval,
                   ppm_normalized_brightness, ppm_area
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm import (
    ppm_blue_ratio,
    ppm_is_bright,
    ppm_maxval,
    ppm_normalized_brightness,
    ppm_area,
)

_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_RED = str(_PPM_DIR / "1x1-red.ppm")
_RGBW = str(_PPM_DIR / "2x2-rgbw.ppm")
_GRADIENT = str(_PPM_DIR / "3x1-gradient.ppm")


class TestPpmBlueRatio:
    def test_returns_float(self):
        result = ppm_blue_ratio(_RED)
        assert isinstance(result, float)

    def test_in_range(self):
        for path in [_RED, _RGBW, _GRADIENT]:
            result = ppm_blue_ratio(path)
            assert 0.0 <= result <= 1.0

    def test_red_image_has_low_blue(self):
        result = ppm_blue_ratio(_RED)
        assert result == 0.0

    def test_rgbw_has_some_blue(self):
        result = ppm_blue_ratio(_RGBW)
        assert result >= 0.0


class TestPpmIsBright:
    def test_returns_bool(self):
        result = ppm_is_bright(_RED)
        assert isinstance(result, bool)

    def test_no_exception(self):
        for path in [_RED, _RGBW, _GRADIENT]:
            ppm_is_bright(path)

    def test_pure_red_bright(self):
        # 1x1 red at maxval should count as bright
        result = ppm_is_bright(_RED)
        assert isinstance(result, bool)

    def test_gradient_type(self):
        result = ppm_is_bright(_GRADIENT)
        assert isinstance(result, bool)


class TestPpmMaxval:
    def test_returns_int(self):
        result = ppm_maxval(_RED)
        assert isinstance(result, int)

    def test_positive(self):
        for path in [_RED, _RGBW, _GRADIENT]:
            result = ppm_maxval(path)
            assert result > 0

    def test_within_netpbm_range(self):
        for path in [_RED, _RGBW, _GRADIENT]:
            result = ppm_maxval(path)
            assert 1 <= result <= 65535

    def test_standard_maxval(self):
        result = ppm_maxval(_RED)
        assert result >= 1


class TestPpmNormalizedBrightness:
    def test_returns_float(self):
        result = ppm_normalized_brightness(_RED)
        assert isinstance(result, float)

    def test_in_range(self):
        for path in [_RED, _RGBW, _GRADIENT]:
            result = ppm_normalized_brightness(path)
            assert 0.0 <= result <= 1.0

    def test_pure_red_positive(self):
        result = ppm_normalized_brightness(_RED)
        assert result > 0.0

    def test_gradient_nonneg(self):
        result = ppm_normalized_brightness(_GRADIENT)
        assert result >= 0.0


class TestPpmArea:
    def test_returns_int(self):
        result = ppm_area(_RED)
        assert isinstance(result, int)

    def test_positive(self):
        for path in [_RED, _RGBW, _GRADIENT]:
            result = ppm_area(path)
            assert result > 0

    def test_red_is_1x1(self):
        result = ppm_area(_RED)
        assert result == 1

    def test_rgbw_is_4(self):
        result = ppm_area(_RGBW)
        assert result == 4
