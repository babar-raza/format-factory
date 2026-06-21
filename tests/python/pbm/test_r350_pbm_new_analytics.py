"""
Sprint 86 — PBM analytics round 3.
25 tests for 5 new analytics functions:
  pbm_black_density_variance, pbm_col_black_variance, pbm_longest_run,
  pbm_top_half_density, pbm_bottom_half_density
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm import (
    pbm_black_density_variance,
    pbm_col_black_variance,
    pbm_longest_run,
    pbm_top_half_density,
    pbm_bottom_half_density,
)

_SAMPLES = _REPO / "samples" / "by-format" / "pbm" / "valid"
_1X1 = str(_SAMPLES / "1x1-black.pbm")
_2X2 = str(_SAMPLES / "2x2-checker.pbm")
_3X2 = str(_SAMPLES / "3x2-pattern.pbm")


# --- pbm_black_density_variance ---

class TestPbmBlackDensityVariance:
    def test_returns_float(self):
        result = pbm_black_density_variance(_3X2)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = pbm_black_density_variance(_3X2)
        assert result >= 0.0

    def test_1x1_is_zero(self):
        result = pbm_black_density_variance(_1X1)
        assert result == 0.0

    def test_2x2_checker(self):
        result = pbm_black_density_variance(_2X2)
        assert isinstance(result, float) and result >= 0.0

    def test_3x2_pattern(self):
        result = pbm_black_density_variance(_3X2)
        assert result >= 0.0


# --- pbm_col_black_variance ---

class TestPbmColBlackVariance:
    def test_returns_float(self):
        result = pbm_col_black_variance(_3X2)
        assert isinstance(result, float)

    def test_non_negative(self):
        result = pbm_col_black_variance(_3X2)
        assert result >= 0.0

    def test_1x1_is_zero(self):
        result = pbm_col_black_variance(_1X1)
        assert result == 0.0

    def test_2x2_checker(self):
        result = pbm_col_black_variance(_2X2)
        assert isinstance(result, float) and result >= 0.0

    def test_3x2_pattern(self):
        result = pbm_col_black_variance(_3X2)
        assert result >= 0.0


# --- pbm_longest_run ---

class TestPbmLongestRun:
    def test_returns_int(self):
        result = pbm_longest_run(_3X2)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = pbm_longest_run(_3X2)
        assert result >= 0

    def test_1x1_black_is_1(self):
        result = pbm_longest_run(_1X1)
        assert result == 1

    def test_2x2_at_most_2(self):
        result = pbm_longest_run(_2X2)
        assert 0 <= result <= 2

    def test_3x2_at_most_3(self):
        result = pbm_longest_run(_3X2)
        assert 0 <= result <= 3


# --- pbm_top_half_density ---

class TestPbmTopHalfDensity:
    def test_returns_float(self):
        result = pbm_top_half_density(_3X2)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = pbm_top_half_density(_3X2)
        assert 0.0 <= result <= 1.0

    def test_1x1_black(self):
        result = pbm_top_half_density(_1X1)
        assert isinstance(result, float) and result == 1.0

    def test_2x2(self):
        result = pbm_top_half_density(_2X2)
        assert 0.0 <= result <= 1.0

    def test_3x2_pattern(self):
        result = pbm_top_half_density(_3X2)
        assert 0.0 <= result <= 1.0


# --- pbm_bottom_half_density ---

class TestPbmBottomHalfDensity:
    def test_returns_float(self):
        result = pbm_bottom_half_density(_3X2)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = pbm_bottom_half_density(_3X2)
        assert 0.0 <= result <= 1.0

    def test_2x2(self):
        result = pbm_bottom_half_density(_2X2)
        assert 0.0 <= result <= 1.0

    def test_3x2_pattern(self):
        result = pbm_bottom_half_density(_3X2)
        assert 0.0 <= result <= 1.0

    def test_1x1_is_zero_or_float(self):
        result = pbm_bottom_half_density(_1X1)
        assert isinstance(result, float)
