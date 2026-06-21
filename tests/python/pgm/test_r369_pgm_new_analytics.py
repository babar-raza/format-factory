"""
Sprint 105 — PGM analytics round 4.
25 tests for 5 new analytics functions:
  pgm_pixel_sum, pgm_dark_pixel_ratio, pgm_bright_pixel_ratio,
  pgm_aspect_ratio, pgm_maxval_minus_avg
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm import (
    pgm_pixel_sum,
    pgm_dark_pixel_ratio,
    pgm_bright_pixel_ratio,
    pgm_aspect_ratio,
    pgm_maxval_minus_avg,
)

_SAMPLES = _REPO / "samples" / "by-format" / "pgm" / "valid"
_WHITE = str(_SAMPLES / "1x1-white.pgm")
_GRAD = str(_SAMPLES / "2x2-gradient.pgm")
_RAMP = str(_SAMPLES / "3x1-ramp.pgm")


# --- pgm_pixel_sum ---

class TestPgmPixelSum:
    def test_returns_int(self):
        result = pgm_pixel_sum(_WHITE)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = pgm_pixel_sum(_WHITE)
        assert result >= 0

    def test_white_positive(self):
        # 1x1 white pixel has value 255
        result = pgm_pixel_sum(_WHITE)
        assert result > 0

    def test_gradient_positive(self):
        result = pgm_pixel_sum(_GRAD)
        assert result > 0

    def test_ramp_positive(self):
        result = pgm_pixel_sum(_RAMP)
        assert result > 0


# --- pgm_dark_pixel_ratio ---

class TestPgmDarkPixelRatio:
    def test_returns_float(self):
        result = pgm_dark_pixel_ratio(_WHITE)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = pgm_dark_pixel_ratio(_WHITE)
        assert 0.0 <= result <= 1.0

    def test_white_is_zero(self):
        # 1x1 white: value=255, threshold=64 → no dark pixels
        result = pgm_dark_pixel_ratio(_WHITE)
        assert result == 0.0

    def test_gradient_bounded(self):
        result = pgm_dark_pixel_ratio(_GRAD)
        assert 0.0 <= result <= 1.0

    def test_ramp_bounded(self):
        result = pgm_dark_pixel_ratio(_RAMP)
        assert 0.0 <= result <= 1.0


# --- pgm_bright_pixel_ratio ---

class TestPgmBrightPixelRatio:
    def test_returns_float(self):
        result = pgm_bright_pixel_ratio(_WHITE)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = pgm_bright_pixel_ratio(_WHITE)
        assert 0.0 <= result <= 1.0

    def test_white_positive(self):
        # 1x1 white: value=255 > threshold=192 → 1.0
        result = pgm_bright_pixel_ratio(_WHITE)
        assert result > 0.0

    def test_gradient_bounded(self):
        result = pgm_bright_pixel_ratio(_GRAD)
        assert 0.0 <= result <= 1.0

    def test_sum_with_dark_lte_one(self):
        dark = pgm_dark_pixel_ratio(_GRAD)
        bright = pgm_bright_pixel_ratio(_GRAD)
        assert dark + bright <= 1.0 + 1e-9


# --- pgm_aspect_ratio ---

class TestPgmAspectRatio:
    def test_returns_float(self):
        result = pgm_aspect_ratio(_WHITE)
        assert isinstance(result, float)

    def test_positive(self):
        result = pgm_aspect_ratio(_WHITE)
        assert result > 0.0

    def test_1x1_is_one(self):
        result = pgm_aspect_ratio(_WHITE)
        assert abs(result - 1.0) < 0.01

    def test_2x2_is_one(self):
        result = pgm_aspect_ratio(_GRAD)
        assert abs(result - 1.0) < 0.01

    def test_3x1_is_three(self):
        # 3 wide, 1 tall → ratio = 3.0
        result = pgm_aspect_ratio(_RAMP)
        assert abs(result - 3.0) < 0.01


# --- pgm_maxval_minus_avg ---

class TestPgmMaxvalMinusAvg:
    def test_returns_float(self):
        result = pgm_maxval_minus_avg(_WHITE)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = pgm_maxval_minus_avg(_WHITE)
        assert result >= 0.0

    def test_white_is_zero(self):
        # 1x1 white: avg=255, maxval=255 → diff=0
        result = pgm_maxval_minus_avg(_WHITE)
        assert result == 0.0

    def test_gradient_non_negative(self):
        result = pgm_maxval_minus_avg(_GRAD)
        assert result >= 0.0

    def test_ramp_non_negative(self):
        result = pgm_maxval_minus_avg(_RAMP)
        assert result >= 0.0
