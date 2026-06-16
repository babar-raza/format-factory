"""
tests/python/qoi/test_r294_qoi_new_analytics.py

Sprint: PRODUCT-DEEPENING-SPRINT-30-20260616
New QOI analytics: qoi_normalized_brightness, qoi_min_brightness,
                   qoi_above_mean_ratio, qoi_green_blue_ratio, qoi_is_wide
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from qoi import (
    qoi_normalized_brightness,
    qoi_min_brightness,
    qoi_above_mean_ratio,
    qoi_green_blue_ratio,
    qoi_is_wide,
)

_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_QOI_DIR / "1x1-red.qoi")
_BLACK = str(_QOI_DIR / "2x2-black.qoi")
_GRADIENT = str(_QOI_DIR / "4x1-gradient.qoi")


class TestQoiNormalizedBrightness:
    def test_returns_float(self):
        result = qoi_normalized_brightness(_RED)
        assert isinstance(result, float)

    def test_in_range(self):
        for path in [_RED, _BLACK, _GRADIENT]:
            result = qoi_normalized_brightness(path)
            assert 0.0 <= result <= 1.0

    def test_black_image_zero(self):
        result = qoi_normalized_brightness(_BLACK)
        assert result == 0.0

    def test_red_image_positive(self):
        result = qoi_normalized_brightness(_RED)
        assert result > 0.0


class TestQoiMinBrightness:
    def test_returns_float(self):
        result = qoi_min_brightness(_RED)
        assert isinstance(result, float)

    def test_nonneg(self):
        for path in [_RED, _BLACK, _GRADIENT]:
            result = qoi_min_brightness(path)
            assert result >= 0.0

    def test_black_image_zero(self):
        result = qoi_min_brightness(_BLACK)
        assert result == 0.0

    def test_red_image_positive(self):
        result = qoi_min_brightness(_RED)
        assert result > 0.0


class TestQoiAboveMeanRatio:
    def test_returns_float(self):
        result = qoi_above_mean_ratio(_GRADIENT)
        assert isinstance(result, float)

    def test_in_range(self):
        for path in [_RED, _BLACK, _GRADIENT]:
            result = qoi_above_mean_ratio(path)
            assert 0.0 <= result <= 1.0

    def test_uniform_image_zero(self):
        # All pixels the same → none above mean
        result = qoi_above_mean_ratio(_RED)
        assert result == 0.0

    def test_black_uniform_zero(self):
        result = qoi_above_mean_ratio(_BLACK)
        assert result == 0.0


class TestQoiGreenBlueRatio:
    def test_returns_float(self):
        result = qoi_green_blue_ratio(_RED)
        assert isinstance(result, float)

    def test_nonneg(self):
        for path in [_RED, _BLACK, _GRADIENT]:
            result = qoi_green_blue_ratio(path)
            assert result >= 0.0

    def test_red_has_no_blue_returns_zero(self):
        # Pure red pixel has blue=0 → ratio is 0.0
        result = qoi_green_blue_ratio(_RED)
        assert result == 0.0

    def test_gradient_nonneg(self):
        result = qoi_green_blue_ratio(_GRADIENT)
        assert result >= 0.0


class TestQoiIsWide:
    def test_returns_bool(self):
        result = qoi_is_wide(_RED)
        assert isinstance(result, bool)

    def test_no_exception(self):
        for path in [_RED, _BLACK, _GRADIENT]:
            qoi_is_wide(path)

    def test_1x1_not_wide(self):
        result = qoi_is_wide(_RED)
        assert result is False

    def test_2x2_not_wide(self):
        result = qoi_is_wide(_BLACK)
        assert result is False
