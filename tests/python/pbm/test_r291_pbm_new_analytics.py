"""Tests for 5 new PBM analytics functions.

Uses real sample files from samples/by-format/pbm/valid/.
Covers: pbm_total_pixels, pbm_aspect_ratio, pbm_is_square,
    pbm_white_density, pbm_is_all_black.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm import (
    pbm_total_pixels,
    pbm_aspect_ratio,
    pbm_is_square,
    pbm_white_density,
    pbm_is_all_black,
)

_SAMPLES = _REPO / "samples" / "by-format" / "pbm" / "valid"
BLACK = _SAMPLES / "1x1-black.pbm"
CHECKER = _SAMPLES / "2x2-checker.pbm"
PATTERN = _SAMPLES / "3x2-pattern.pbm"


class TestPbmTotalPixels:
    def test_returns_int(self):
        result = pbm_total_pixels(BLACK)
        assert isinstance(result, int)

    def test_1x1_is_1(self):
        assert pbm_total_pixels(BLACK) == 1

    def test_2x2_is_4(self):
        assert pbm_total_pixels(CHECKER) == 4

    def test_3x2_is_6(self):
        assert pbm_total_pixels(PATTERN) == 6


class TestPbmAspectRatio:
    def test_returns_float(self):
        result = pbm_aspect_ratio(BLACK)
        assert isinstance(result, float)

    def test_1x1_is_one(self):
        assert pbm_aspect_ratio(BLACK) == 1.0

    def test_2x2_is_one(self):
        assert pbm_aspect_ratio(CHECKER) == 1.0

    def test_3x2_is_1_5(self):
        result = pbm_aspect_ratio(PATTERN)
        assert result == pytest.approx(1.5)


class TestPbmIsSquare:
    def test_returns_bool(self):
        result = pbm_is_square(BLACK)
        assert isinstance(result, bool)

    def test_1x1_is_square(self):
        assert pbm_is_square(BLACK) is True

    def test_2x2_is_square(self):
        assert pbm_is_square(CHECKER) is True

    def test_3x2_not_square(self):
        assert pbm_is_square(PATTERN) is False


class TestPbmWhiteDensity:
    def test_returns_float(self):
        result = pbm_white_density(BLACK)
        assert isinstance(result, float)

    def test_in_range(self):
        result = pbm_white_density(CHECKER)
        assert 0.0 <= result <= 1.0

    def test_all_black_is_zero(self):
        result = pbm_white_density(BLACK)
        assert result == 0.0


class TestPbmIsAllBlack:
    def test_returns_bool(self):
        result = pbm_is_all_black(BLACK)
        assert isinstance(result, bool)

    def test_black_is_all_black(self):
        assert pbm_is_all_black(BLACK) is True

    def test_checker_is_not_all_black(self):
        assert pbm_is_all_black(CHECKER) is False
