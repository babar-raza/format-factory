"""
Sprint 88 — PPM analytics round 3.
25 tests for 5 new analytics functions:
  ppm_red_variance, ppm_green_variance, ppm_blue_variance,
  ppm_entropy, ppm_top_half_brightness
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm import (
    ppm_red_variance,
    ppm_green_variance,
    ppm_blue_variance,
    ppm_entropy,
    ppm_top_half_brightness,
)

_SAMPLES = _REPO / "samples" / "by-format" / "ppm" / "valid"
_1X1 = str(_SAMPLES / "1x1-red.ppm")
_2X2 = str(_SAMPLES / "2x2-rgbw.ppm")
_3X1 = str(_SAMPLES / "3x1-gradient.ppm")


# --- ppm_red_variance ---

class TestPpmRedVariance:
    def test_returns_float(self):
        result = ppm_red_variance(_2X2)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = ppm_red_variance(_2X2)
        assert result >= 0.0

    def test_1x1_single_pixel_zero(self):
        result = ppm_red_variance(_1X1)
        assert result == 0.0

    def test_gradient(self):
        result = ppm_red_variance(_3X1)
        assert isinstance(result, float) and result >= 0.0

    def test_rgbw_2x2(self):
        result = ppm_red_variance(_2X2)
        assert result >= 0.0


# --- ppm_green_variance ---

class TestPpmGreenVariance:
    def test_returns_float(self):
        result = ppm_green_variance(_2X2)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = ppm_green_variance(_2X2)
        assert result >= 0.0

    def test_1x1_red_is_zero(self):
        result = ppm_green_variance(_1X1)
        assert result == 0.0

    def test_gradient(self):
        result = ppm_green_variance(_3X1)
        assert isinstance(result, float) and result >= 0.0

    def test_rgbw_2x2(self):
        result = ppm_green_variance(_2X2)
        assert result >= 0.0


# --- ppm_blue_variance ---

class TestPpmBlueVariance:
    def test_returns_float(self):
        result = ppm_blue_variance(_2X2)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = ppm_blue_variance(_2X2)
        assert result >= 0.0

    def test_1x1_red_is_zero(self):
        result = ppm_blue_variance(_1X1)
        assert result == 0.0

    def test_gradient(self):
        result = ppm_blue_variance(_3X1)
        assert isinstance(result, float) and result >= 0.0

    def test_rgbw_2x2(self):
        result = ppm_blue_variance(_2X2)
        assert result >= 0.0


# --- ppm_entropy ---

class TestPpmEntropy:
    def test_returns_float(self):
        result = ppm_entropy(_2X2)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = ppm_entropy(_2X2)
        assert result >= 0.0

    def test_1x1_zero_entropy(self):
        result = ppm_entropy(_1X1)
        assert result == 0.0

    def test_bounded_by_8(self):
        result = ppm_entropy(_2X2)
        assert result <= 8.0

    def test_gradient_non_zero(self):
        result = ppm_entropy(_3X1)
        assert isinstance(result, float) and result >= 0.0


# --- ppm_top_half_brightness ---

class TestPpmTopHalfBrightness:
    def test_returns_float(self):
        result = ppm_top_half_brightness(_2X2)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = ppm_top_half_brightness(_2X2)
        assert result >= 0.0

    def test_bounded_by_255(self):
        result = ppm_top_half_brightness(_2X2)
        assert result <= 255.0

    def test_1x1_red(self):
        result = ppm_top_half_brightness(_1X1)
        assert isinstance(result, float) and result >= 0.0

    def test_gradient(self):
        result = ppm_top_half_brightness(_3X1)
        assert isinstance(result, float) and result >= 0.0
