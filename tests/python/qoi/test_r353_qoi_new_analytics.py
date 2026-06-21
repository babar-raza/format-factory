"""
Sprint 89 — QOI analytics round 3.
25 tests for 5 new analytics functions:
  qoi_red_variance, qoi_green_variance, qoi_blue_variance,
  qoi_entropy, qoi_top_half_brightness
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi import (
    qoi_red_variance,
    qoi_green_variance,
    qoi_blue_variance,
    qoi_entropy,
    qoi_top_half_brightness,
)

_SAMPLES = _REPO / "samples" / "by-format" / "qoi" / "valid"
_1X1 = str(_SAMPLES / "1x1-red.qoi")
_2X2 = str(_SAMPLES / "2x2-black.qoi")
_4X1 = str(_SAMPLES / "4x1-gradient.qoi")


# --- qoi_red_variance ---

class TestQoiRedVariance:
    def test_returns_float(self):
        result = qoi_red_variance(_4X1)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = qoi_red_variance(_4X1)
        assert result >= 0.0

    def test_1x1_single_pixel_zero(self):
        result = qoi_red_variance(_1X1)
        assert result == 0.0

    def test_2x2_black(self):
        result = qoi_red_variance(_2X2)
        assert result == 0.0

    def test_gradient(self):
        result = qoi_red_variance(_4X1)
        assert result >= 0.0


# --- qoi_green_variance ---

class TestQoiGreenVariance:
    def test_returns_float(self):
        result = qoi_green_variance(_4X1)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = qoi_green_variance(_4X1)
        assert result >= 0.0

    def test_1x1_zero(self):
        result = qoi_green_variance(_1X1)
        assert result == 0.0

    def test_2x2_black(self):
        result = qoi_green_variance(_2X2)
        assert result == 0.0

    def test_gradient(self):
        result = qoi_green_variance(_4X1)
        assert result >= 0.0


# --- qoi_blue_variance ---

class TestQoiBlueVariance:
    def test_returns_float(self):
        result = qoi_blue_variance(_4X1)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = qoi_blue_variance(_4X1)
        assert result >= 0.0

    def test_1x1_zero(self):
        result = qoi_blue_variance(_1X1)
        assert result == 0.0

    def test_2x2_black(self):
        result = qoi_blue_variance(_2X2)
        assert result == 0.0

    def test_gradient(self):
        result = qoi_blue_variance(_4X1)
        assert result >= 0.0


# --- qoi_entropy ---

class TestQoiEntropy:
    def test_returns_float(self):
        result = qoi_entropy(_4X1)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = qoi_entropy(_4X1)
        assert result >= 0.0

    def test_1x1_single_pixel_zero(self):
        result = qoi_entropy(_1X1)
        assert result == 0.0

    def test_bounded_by_8(self):
        result = qoi_entropy(_4X1)
        assert result <= 8.0

    def test_2x2_black(self):
        result = qoi_entropy(_2X2)
        assert result == 0.0


# --- qoi_top_half_brightness ---

class TestQoiTopHalfBrightness:
    def test_returns_float(self):
        result = qoi_top_half_brightness(_4X1)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = qoi_top_half_brightness(_4X1)
        assert result >= 0.0

    def test_bounded_by_255(self):
        result = qoi_top_half_brightness(_4X1)
        assert result <= 255.0

    def test_1x1_red(self):
        result = qoi_top_half_brightness(_1X1)
        assert isinstance(result, float) and result >= 0.0

    def test_2x2_black(self):
        result = qoi_top_half_brightness(_2X2)
        assert result == 0.0
