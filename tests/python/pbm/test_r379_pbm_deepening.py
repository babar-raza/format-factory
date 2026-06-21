"""Tests for PBM product deepening sprint 150.

New functions:
  pbm_total_pixels_minus_white — total pixel count minus white pixels (= black count)
  pbm_width_plus_height        — canvas width plus canvas height
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_total_pixels_minus_white, pbm_width_plus_height

_BLACK = str(_REPO / "samples" / "by-format" / "pbm" / "valid" / "1x1-black.pbm")
_CHECKER = str(_REPO / "samples" / "by-format" / "pbm" / "valid" / "2x2-checker.pbm")
_PATTERN = str(_REPO / "samples" / "by-format" / "pbm" / "valid" / "3x2-pattern.pbm")


class TestPbmTotalPixelsMinusWhite:
    def test_return_type(self):
        assert isinstance(pbm_total_pixels_minus_white(_BLACK), int)

    def test_exact_1_for_black(self):
        # 1x1-black.pbm: 1 total, 0 white → 1
        assert pbm_total_pixels_minus_white(_BLACK) == 1

    def test_exact_2_for_checker(self):
        # 2x2-checker.pbm: 4 total, 2 white → 2
        assert pbm_total_pixels_minus_white(_CHECKER) == 2

    def test_exact_3_for_pattern(self):
        # 3x2-pattern.pbm: 6 total, 3 white → 3
        assert pbm_total_pixels_minus_white(_PATTERN) == 3

    def test_nonnegative(self):
        assert pbm_total_pixels_minus_white(_BLACK) >= 0

    def test_consistent(self):
        assert pbm_total_pixels_minus_white(_CHECKER) == pbm_total_pixels_minus_white(_CHECKER)


class TestPbmWidthPlusHeight:
    def test_return_type(self):
        assert isinstance(pbm_width_plus_height(_BLACK), int)

    def test_exact_2_for_black(self):
        # 1x1-black.pbm: 1 + 1 = 2
        assert pbm_width_plus_height(_BLACK) == 2

    def test_exact_4_for_checker(self):
        # 2x2-checker.pbm: 2 + 2 = 4
        assert pbm_width_plus_height(_CHECKER) == 4

    def test_exact_5_for_pattern(self):
        # 3x2-pattern.pbm: 3 + 2 = 5
        assert pbm_width_plus_height(_PATTERN) == 5

    def test_positive(self):
        assert pbm_width_plus_height(_BLACK) > 0

    def test_consistent(self):
        assert pbm_width_plus_height(_PATTERN) == pbm_width_plus_height(_PATTERN)
