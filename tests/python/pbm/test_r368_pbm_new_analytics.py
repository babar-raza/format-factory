"""
Sprint 104 — PBM analytics round 4.
25 tests for 5 new analytics functions:
  pbm_black_minus_white, pbm_white_density, pbm_is_all_black,
  pbm_is_all_white, pbm_aspect_ratio
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm import (
    pbm_black_minus_white,
    pbm_white_density,
    pbm_is_all_black,
    pbm_is_all_white,
    pbm_aspect_ratio,
)

_SAMPLES = _REPO / "samples" / "by-format" / "pbm" / "valid"
_BLACK = str(_SAMPLES / "1x1-black.pbm")
_CHECKER = str(_SAMPLES / "2x2-checker.pbm")
_PATTERN = str(_SAMPLES / "3x2-pattern.pbm")


# --- pbm_black_minus_white ---

class TestPbmBlackMinusWhite:
    def test_returns_int(self):
        result = pbm_black_minus_white(_BLACK)
        assert isinstance(result, int)

    def test_all_black_positive(self):
        # 1x1 black: 1 black, 0 white → diff = 1
        result = pbm_black_minus_white(_BLACK)
        assert result > 0

    def test_checker_near_zero(self):
        # 2x2 checker: 2 black, 2 white → diff = 0
        result = pbm_black_minus_white(_CHECKER)
        assert result == 0

    def test_pattern_is_int(self):
        result = pbm_black_minus_white(_PATTERN)
        assert isinstance(result, int)

    def test_result_can_be_negative_or_positive(self):
        result = pbm_black_minus_white(_PATTERN)
        assert isinstance(result, int)


# --- pbm_white_density ---

class TestPbmWhiteDensity:
    def test_returns_float(self):
        result = pbm_white_density(_BLACK)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = pbm_white_density(_BLACK)
        assert 0.0 <= result <= 1.0

    def test_all_black_is_zero(self):
        # 1x1 black: 0 white pixels
        result = pbm_white_density(_BLACK)
        assert result == 0.0

    def test_checker_half(self):
        # 2x2 checker: 2 white, 2 black → 0.5
        result = pbm_white_density(_CHECKER)
        assert abs(result - 0.5) < 0.01

    def test_pattern_bounded(self):
        result = pbm_white_density(_PATTERN)
        assert 0.0 <= result <= 1.0


# --- pbm_is_all_black ---

class TestPbmIsAllBlack:
    def test_returns_bool(self):
        result = pbm_is_all_black(_BLACK)
        assert isinstance(result, bool)

    def test_1x1_black_is_true(self):
        result = pbm_is_all_black(_BLACK)
        assert result is True

    def test_checker_is_false(self):
        result = pbm_is_all_black(_CHECKER)
        assert result is False

    def test_pattern_is_false(self):
        result = pbm_is_all_black(_PATTERN)
        assert result is False

    def test_consistent_with_white_density(self):
        # if all black, white_density == 0
        result = pbm_is_all_black(_BLACK)
        density = pbm_white_density(_BLACK)
        if result:
            assert density == 0.0


# --- pbm_is_all_white ---

class TestPbmIsAllWhite:
    def test_returns_bool(self):
        result = pbm_is_all_white(_BLACK)
        assert isinstance(result, bool)

    def test_1x1_black_is_false(self):
        result = pbm_is_all_white(_BLACK)
        assert result is False

    def test_checker_is_false(self):
        result = pbm_is_all_white(_CHECKER)
        assert result is False

    def test_pattern_is_false(self):
        result = pbm_is_all_white(_PATTERN)
        assert result is False

    def test_not_both_all_black_and_all_white(self):
        # Can't be both all-black and all-white for same file
        ab = pbm_is_all_black(_CHECKER)
        aw = pbm_is_all_white(_CHECKER)
        assert not (ab and aw)


# --- pbm_aspect_ratio ---

class TestPbmAspectRatio:
    def test_returns_float(self):
        result = pbm_aspect_ratio(_BLACK)
        assert isinstance(result, float)

    def test_1x1_is_one(self):
        # 1x1 → ratio = 1.0
        result = pbm_aspect_ratio(_BLACK)
        assert abs(result - 1.0) < 0.01

    def test_2x2_is_one(self):
        result = pbm_aspect_ratio(_CHECKER)
        assert abs(result - 1.0) < 0.01

    def test_3x2_is_1_5(self):
        # 3 wide, 2 tall → 1.5
        result = pbm_aspect_ratio(_PATTERN)
        assert abs(result - 1.5) < 0.01

    def test_positive(self):
        result = pbm_aspect_ratio(_BLACK)
        assert result > 0.0
