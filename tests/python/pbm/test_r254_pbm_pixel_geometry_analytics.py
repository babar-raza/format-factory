"""Tests for PBM pixel and geometry analytics (Sprint 39).

Closes:
  GAP-PBM-FOSS-PBM_HAS_ANY_-001  (Pbm Has Any Black)
  GAP-PBM-FOSS-PBM_BLACK_PI-001  (Pbm Black Pixel Count)
  GAP-PBM-FOSS-PBM_IS_UNIFO-001  (Pbm Is Uniform)
  GAP-PBM-FOSS-PBM_PERIMETE-001  (Pbm Perimeter)
  GAP-PBM-FOSS-PBM_IS_SQUAR-001  (Pbm Is Square)
  GAP-PBM-FOSS-PBM_IS_LANDS-001  (Pbm Is Landscape)
  GAP-PBM-FOSS-PBM_MAX_ROW_-001  (Pbm Max Row Black Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import (
    pbm_black_pixel_count,
    pbm_has_any_black,
    pbm_is_landscape,
    pbm_is_square,
    pbm_is_uniform,
    pbm_max_row_black_count,
    pbm_perimeter,
)

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_1X1_BLACK = str(_DIR / "1x1-black.pbm")       # 1 pixel, all black
_2X2_CHECK = str(_DIR / "2x2-checker.pbm")     # 2x2 checkerboard (B,W,W,B)
_3X2_PAT = str(_DIR / "3x2-pattern.pbm")       # 3 wide x 2 high, 3 black pixels


class TestPbmHasAnyBlack:
    def test_return_type(self):
        assert isinstance(pbm_has_any_black(_1X1_BLACK), bool)

    def test_true_for_1x1_black(self):
        assert pbm_has_any_black(_1X1_BLACK) is True

    def test_true_for_2x2_checker(self):
        # checker has black pixels
        assert pbm_has_any_black(_2X2_CHECK) is True

    def test_true_for_3x2_pattern(self):
        assert pbm_has_any_black(_3X2_PAT) is True

    def test_consistent_across_calls(self):
        assert pbm_has_any_black(_1X1_BLACK) == pbm_has_any_black(_1X1_BLACK)


class TestPbmBlackPixelCount:
    def test_return_type(self):
        assert isinstance(pbm_black_pixel_count(_1X1_BLACK), int)

    def test_exact_1_for_1x1_black(self):
        # 1 pixel, all black
        assert pbm_black_pixel_count(_1X1_BLACK) == 1

    def test_exact_2_for_2x2_checker(self):
        # 2 black pixels out of 4
        assert pbm_black_pixel_count(_2X2_CHECK) == 2

    def test_exact_3_for_3x2_pattern(self):
        # 3 black pixels
        assert pbm_black_pixel_count(_3X2_PAT) == 3

    def test_nonnegative(self):
        assert pbm_black_pixel_count(_1X1_BLACK) >= 0

    def test_consistent_across_calls(self):
        assert pbm_black_pixel_count(_1X1_BLACK) == pbm_black_pixel_count(_1X1_BLACK)


class TestPbmIsUniform:
    def test_return_type(self):
        assert isinstance(pbm_is_uniform(_1X1_BLACK), bool)

    def test_true_for_1x1_black(self):
        # Only 1 pixel -> uniform by definition
        assert pbm_is_uniform(_1X1_BLACK) is True

    def test_false_for_2x2_checker(self):
        # Mix of black and white
        assert pbm_is_uniform(_2X2_CHECK) is False

    def test_false_for_3x2_pattern(self):
        assert pbm_is_uniform(_3X2_PAT) is False

    def test_consistent_across_calls(self):
        assert pbm_is_uniform(_1X1_BLACK) == pbm_is_uniform(_1X1_BLACK)


class TestPbmPerimeter:
    def test_return_type(self):
        assert isinstance(pbm_perimeter(_1X1_BLACK), int)

    def test_exact_4_for_1x1(self):
        # 2*(1+1) = 4
        assert pbm_perimeter(_1X1_BLACK) == 4

    def test_exact_8_for_2x2(self):
        # 2*(2+2) = 8
        assert pbm_perimeter(_2X2_CHECK) == 8

    def test_exact_10_for_3x2(self):
        # 2*(3+2) = 10
        assert pbm_perimeter(_3X2_PAT) == 10

    def test_nonnegative(self):
        assert pbm_perimeter(_1X1_BLACK) >= 0

    def test_consistent_across_calls(self):
        assert pbm_perimeter(_1X1_BLACK) == pbm_perimeter(_1X1_BLACK)


class TestPbmIsSquare:
    def test_return_type(self):
        assert isinstance(pbm_is_square(_1X1_BLACK), bool)

    def test_true_for_1x1(self):
        assert pbm_is_square(_1X1_BLACK) is True

    def test_true_for_2x2(self):
        assert pbm_is_square(_2X2_CHECK) is True

    def test_false_for_3x2(self):
        # 3 wide x 2 high is not square
        assert pbm_is_square(_3X2_PAT) is False

    def test_consistent_across_calls(self):
        assert pbm_is_square(_1X1_BLACK) == pbm_is_square(_1X1_BLACK)


class TestPbmIsLandscape:
    def test_return_type(self):
        assert isinstance(pbm_is_landscape(_1X1_BLACK), bool)

    def test_false_for_1x1_square(self):
        assert pbm_is_landscape(_1X1_BLACK) is False

    def test_false_for_2x2_square(self):
        assert pbm_is_landscape(_2X2_CHECK) is False

    def test_true_for_3x2(self):
        # 3 wide x 2 high: width > height -> landscape
        assert pbm_is_landscape(_3X2_PAT) is True

    def test_consistent_across_calls(self):
        assert pbm_is_landscape(_3X2_PAT) == pbm_is_landscape(_3X2_PAT)


class TestPbmMaxRowBlackCount:
    def test_return_type(self):
        assert isinstance(pbm_max_row_black_count(_1X1_BLACK), int)

    def test_exact_1_for_1x1_black(self):
        # 1 row with 1 black pixel
        assert pbm_max_row_black_count(_1X1_BLACK) == 1

    def test_exact_1_for_2x2_checker(self):
        # Each row has 1 black pixel (checkerboard: BW, WB)
        assert pbm_max_row_black_count(_2X2_CHECK) == 1

    def test_exact_2_for_3x2_pattern(self):
        # 3x2 pattern: one row has 2 black pixels
        assert pbm_max_row_black_count(_3X2_PAT) == 2

    def test_nonnegative(self):
        assert pbm_max_row_black_count(_1X1_BLACK) >= 0

    def test_consistent_across_calls(self):
        assert pbm_max_row_black_count(_1X1_BLACK) == pbm_max_row_black_count(_1X1_BLACK)
