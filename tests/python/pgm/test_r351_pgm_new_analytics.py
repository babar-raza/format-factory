"""
Sprint 87 — PGM analytics round 3.
25 tests for 5 new analytics functions:
  pgm_col_brightness_variance, pgm_top_half_avg, pgm_bottom_half_avg,
  pgm_pixel_entropy, pgm_mid_pixel_ratio
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm import (
    pgm_col_brightness_variance,
    pgm_top_half_avg,
    pgm_bottom_half_avg,
    pgm_pixel_entropy,
    pgm_mid_pixel_ratio,
)

_SAMPLES = _REPO / "samples" / "by-format" / "pgm" / "valid"
_1X1 = str(_SAMPLES / "1x1-white.pgm")
_2X2 = str(_SAMPLES / "2x2-gradient.pgm")
_3X1 = str(_SAMPLES / "3x1-ramp.pgm")


# --- pgm_col_brightness_variance ---

class TestPgmColBrightnessVariance:
    def test_returns_float(self):
        result = pgm_col_brightness_variance(_2X2)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = pgm_col_brightness_variance(_2X2)
        assert result >= 0.0

    def test_1x1_is_zero(self):
        result = pgm_col_brightness_variance(_1X1)
        assert result == 0.0

    def test_gradient_2x2(self):
        result = pgm_col_brightness_variance(_2X2)
        assert result >= 0.0

    def test_ramp_3x1(self):
        result = pgm_col_brightness_variance(_3X1)
        assert isinstance(result, float) and result >= 0.0


# --- pgm_top_half_avg ---

class TestPgmTopHalfAvg:
    def test_returns_float(self):
        result = pgm_top_half_avg(_2X2)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = pgm_top_half_avg(_2X2)
        assert result >= 0.0

    def test_1x1_white(self):
        result = pgm_top_half_avg(_1X1)
        assert result >= 0.0

    def test_bounded_by_255(self):
        result = pgm_top_half_avg(_2X2)
        assert result <= 255.0

    def test_3x1_ramp(self):
        result = pgm_top_half_avg(_3X1)
        assert isinstance(result, float) and result >= 0.0


# --- pgm_bottom_half_avg ---

class TestPgmBottomHalfAvg:
    def test_returns_float(self):
        result = pgm_bottom_half_avg(_2X2)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = pgm_bottom_half_avg(_2X2)
        assert result >= 0.0

    def test_bounded_by_255(self):
        result = pgm_bottom_half_avg(_2X2)
        assert result <= 255.0

    def test_1x1_single_row_is_zero(self):
        result = pgm_bottom_half_avg(_1X1)
        assert result == 0.0

    def test_gradient_2x2(self):
        result = pgm_bottom_half_avg(_2X2)
        assert isinstance(result, float)


# --- pgm_pixel_entropy ---

class TestPgmPixelEntropy:
    def test_returns_float(self):
        result = pgm_pixel_entropy(_2X2)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = pgm_pixel_entropy(_2X2)
        assert result >= 0.0

    def test_1x1_white_is_zero(self):
        result = pgm_pixel_entropy(_1X1)
        assert result == 0.0

    def test_bounded_by_8(self):
        result = pgm_pixel_entropy(_2X2)
        assert result <= 8.0

    def test_gradient_positive(self):
        result = pgm_pixel_entropy(_2X2)
        assert result >= 0.0


# --- pgm_mid_pixel_ratio ---

class TestPgmMidPixelRatio:
    def test_returns_float(self):
        result = pgm_mid_pixel_ratio(_2X2)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = pgm_mid_pixel_ratio(_2X2)
        assert 0.0 <= result <= 1.0

    def test_1x1_white(self):
        result = pgm_mid_pixel_ratio(_1X1)
        assert isinstance(result, float)

    def test_ramp_bounded(self):
        result = pgm_mid_pixel_ratio(_3X1)
        assert 0.0 <= result <= 1.0

    def test_gradient_2x2(self):
        result = pgm_mid_pixel_ratio(_2X2)
        assert 0.0 <= result <= 1.0
