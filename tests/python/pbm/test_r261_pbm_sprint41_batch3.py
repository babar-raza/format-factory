"""Tests for PBM Sprint 41 batch 3 gap closure.

Closes:
  GAP-PBM-FOSS-PBM_CORNER_P-001  (Pbm Corner Pixel Sum)
  GAP-PBM-FOSS-PBM_CHECKERB-001  (Pbm Checkerboard Score)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_checkerboard_score, pbm_corner_pixel_sum

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_1X1_BLACK = str(_DIR / "1x1-black.pbm")
_2X2_CHECKER = str(_DIR / "2x2-checker.pbm")
_3X2_PATTERN = str(_DIR / "3x2-pattern.pbm")


class TestPbmCornerPixelSum:
    def test_return_type(self):
        assert isinstance(pbm_corner_pixel_sum(_1X1_BLACK), int)

    def test_exact_4_for_1x1_black(self):
        assert pbm_corner_pixel_sum(_1X1_BLACK) == 4

    def test_exact_2_for_2x2_checker(self):
        assert pbm_corner_pixel_sum(_2X2_CHECKER) == 2

    def test_nonnegative(self):
        assert pbm_corner_pixel_sum(_1X1_BLACK) >= 0

    def test_consistent_across_calls(self):
        assert pbm_corner_pixel_sum(_1X1_BLACK) == pbm_corner_pixel_sum(_1X1_BLACK)


class TestPbmCheckerboardScore:
    def test_return_type(self):
        assert isinstance(pbm_checkerboard_score(_1X1_BLACK), float)

    def test_exact_0_0_for_1x1_black(self):
        assert pbm_checkerboard_score(_1X1_BLACK) == 0.0

    def test_exact_1_0_for_2x2_checker(self):
        assert pbm_checkerboard_score(_2X2_CHECKER) == 1.0

    def test_nonnegative(self):
        assert pbm_checkerboard_score(_1X1_BLACK) >= 0.0

    def test_consistent_across_calls(self):
        assert pbm_checkerboard_score(_1X1_BLACK) == pbm_checkerboard_score(_1X1_BLACK)
