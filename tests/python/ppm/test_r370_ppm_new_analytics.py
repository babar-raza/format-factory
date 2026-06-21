"""
Sprint 106 — PPM analytics round 4.
25 tests for 5 new analytics functions:
  ppm_pixel_count, ppm_aspect_ratio, ppm_max_channel_value,
  ppm_min_channel_value, ppm_luminance_range
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm import (
    ppm_pixel_count,
    ppm_aspect_ratio,
    ppm_max_channel_value,
    ppm_min_channel_value,
    ppm_luminance_range,
)

_SAMPLES = _REPO / "samples" / "by-format" / "ppm" / "valid"
_RED = str(_SAMPLES / "1x1-red.ppm")
_RGBW = str(_SAMPLES / "2x2-rgbw.ppm")
_GRAD = str(_SAMPLES / "3x1-gradient.ppm")


# --- ppm_pixel_count ---

class TestPpmPixelCount:
    def test_returns_int(self):
        result = ppm_pixel_count(_RED)
        assert isinstance(result, int)

    def test_1x1_is_one(self):
        result = ppm_pixel_count(_RED)
        assert result == 1

    def test_2x2_is_four(self):
        result = ppm_pixel_count(_RGBW)
        assert result == 4

    def test_3x1_is_three(self):
        result = ppm_pixel_count(_GRAD)
        assert result == 3

    def test_positive(self):
        result = ppm_pixel_count(_RED)
        assert result > 0


# --- ppm_aspect_ratio ---

class TestPpmAspectRatio:
    def test_returns_float(self):
        result = ppm_aspect_ratio(_RED)
        assert isinstance(result, float)

    def test_1x1_is_one(self):
        result = ppm_aspect_ratio(_RED)
        assert abs(result - 1.0) < 0.01

    def test_2x2_is_one(self):
        result = ppm_aspect_ratio(_RGBW)
        assert abs(result - 1.0) < 0.01

    def test_3x1_is_three(self):
        result = ppm_aspect_ratio(_GRAD)
        assert abs(result - 3.0) < 0.01

    def test_positive(self):
        result = ppm_aspect_ratio(_RED)
        assert result > 0.0


# --- ppm_max_channel_value ---

class TestPpmMaxChannelValue:
    def test_returns_int(self):
        result = ppm_max_channel_value(_RED)
        assert isinstance(result, int)

    def test_bounded_0_to_255(self):
        result = ppm_max_channel_value(_RED)
        assert 0 <= result <= 255

    def test_red_pixel_has_max_255(self):
        # 1x1 red = (255, 0, 0) → max = 255
        result = ppm_max_channel_value(_RED)
        assert result == 255

    def test_rgbw_is_255(self):
        result = ppm_max_channel_value(_RGBW)
        assert result == 255

    def test_gte_min_channel_value(self):
        mx = ppm_max_channel_value(_RGBW)
        mn = ppm_min_channel_value(_RGBW)
        assert mx >= mn


# --- ppm_min_channel_value ---

class TestPpmMinChannelValue:
    def test_returns_int(self):
        result = ppm_min_channel_value(_RED)
        assert isinstance(result, int)

    def test_bounded_0_to_255(self):
        result = ppm_min_channel_value(_RED)
        assert 0 <= result <= 255

    def test_red_pixel_has_min_0(self):
        # 1x1 red = (255, 0, 0) → min = 0
        result = ppm_min_channel_value(_RED)
        assert result == 0

    def test_rgbw_is_0(self):
        result = ppm_min_channel_value(_RGBW)
        assert result == 0

    def test_lte_max_channel_value(self):
        mn = ppm_min_channel_value(_RED)
        mx = ppm_max_channel_value(_RED)
        assert mn <= mx


# --- ppm_luminance_range ---

class TestPpmLuminanceRange:
    def test_returns_float(self):
        result = ppm_luminance_range(_RED)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = ppm_luminance_range(_RED)
        assert result >= 0.0

    def test_single_pixel_is_zero(self):
        # Only 1 pixel → range = 0
        result = ppm_luminance_range(_RED)
        assert result == 0.0

    def test_rgbw_positive(self):
        # 4 different colored pixels → range > 0
        result = ppm_luminance_range(_RGBW)
        assert result > 0.0

    def test_gradient_non_negative(self):
        result = ppm_luminance_range(_GRAD)
        assert result >= 0.0
