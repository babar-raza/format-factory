"""
Sprint 107 — QOI analytics round 4.
25 tests for 5 new analytics functions:
  qoi_pixel_count, qoi_aspect_ratio, qoi_max_channel_value,
  qoi_min_channel_value, qoi_luminance_range
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi import (
    qoi_pixel_count,
    qoi_aspect_ratio,
    qoi_max_channel_value,
    qoi_min_channel_value,
    qoi_luminance_range,
)

_SAMPLES = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_SAMPLES / "1x1-red.qoi")
_BLACK = str(_SAMPLES / "2x2-black.qoi")
_GRAD = str(_SAMPLES / "4x1-gradient.qoi")


# --- qoi_pixel_count ---

class TestQoiPixelCount:
    def test_returns_int(self):
        result = qoi_pixel_count(_RED)
        assert isinstance(result, int)

    def test_1x1_is_one(self):
        result = qoi_pixel_count(_RED)
        assert result == 1

    def test_2x2_is_four(self):
        result = qoi_pixel_count(_BLACK)
        assert result == 4

    def test_4x1_is_four(self):
        result = qoi_pixel_count(_GRAD)
        assert result == 4

    def test_positive(self):
        result = qoi_pixel_count(_RED)
        assert result > 0


# --- qoi_aspect_ratio ---

class TestQoiAspectRatio:
    def test_returns_float(self):
        result = qoi_aspect_ratio(_RED)
        assert isinstance(result, float)

    def test_1x1_is_one(self):
        result = qoi_aspect_ratio(_RED)
        assert abs(result - 1.0) < 0.01

    def test_2x2_is_one(self):
        result = qoi_aspect_ratio(_BLACK)
        assert abs(result - 1.0) < 0.01

    def test_4x1_is_four(self):
        result = qoi_aspect_ratio(_GRAD)
        assert abs(result - 4.0) < 0.01

    def test_positive(self):
        result = qoi_aspect_ratio(_RED)
        assert result > 0.0


# --- qoi_max_channel_value ---

class TestQoiMaxChannelValue:
    def test_returns_int(self):
        result = qoi_max_channel_value(_RED)
        assert isinstance(result, int)

    def test_bounded_0_to_255(self):
        result = qoi_max_channel_value(_RED)
        assert 0 <= result <= 255

    def test_red_pixel_is_255(self):
        result = qoi_max_channel_value(_RED)
        assert result == 255

    def test_black_is_zero(self):
        result = qoi_max_channel_value(_BLACK)
        assert result == 0

    def test_gte_min_channel_value(self):
        mx = qoi_max_channel_value(_GRAD)
        mn = qoi_min_channel_value(_GRAD)
        assert mx >= mn


# --- qoi_min_channel_value ---

class TestQoiMinChannelValue:
    def test_returns_int(self):
        result = qoi_min_channel_value(_RED)
        assert isinstance(result, int)

    def test_bounded_0_to_255(self):
        result = qoi_min_channel_value(_RED)
        assert 0 <= result <= 255

    def test_red_pixel_has_min_0(self):
        result = qoi_min_channel_value(_RED)
        assert result == 0

    def test_black_is_zero(self):
        result = qoi_min_channel_value(_BLACK)
        assert result == 0

    def test_lte_max_channel_value(self):
        mn = qoi_min_channel_value(_GRAD)
        mx = qoi_max_channel_value(_GRAD)
        assert mn <= mx


# --- qoi_luminance_range ---

class TestQoiLuminanceRange:
    def test_returns_float(self):
        result = qoi_luminance_range(_RED)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = qoi_luminance_range(_RED)
        assert result >= 0.0

    def test_single_pixel_is_zero(self):
        result = qoi_luminance_range(_RED)
        assert result == 0.0

    def test_black_all_same_is_zero(self):
        result = qoi_luminance_range(_BLACK)
        assert result == 0.0

    def test_gradient_non_negative(self):
        result = qoi_luminance_range(_GRAD)
        assert result >= 0.0
