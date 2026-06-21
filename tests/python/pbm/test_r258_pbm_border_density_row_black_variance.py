"""Tests for PBM gap closure batch 3 (Sprint 40).

Closes:
  GAP-PBM-FOSS-PBM_BORDER_D-001   (Pbm Border Density)
  GAP-PBM-FOSS-PBM_ROW_BLAC-001   (Pbm Row Black Variance)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_border_density, pbm_row_black_variance

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_1X1_BLACK = str(_DIR / "1x1-black.pbm")
_2X2_CHECKER = str(_DIR / "2x2-checker.pbm")
_3X2_PATTERN = str(_DIR / "3x2-pattern.pbm")


class TestPbmBorderDensity:
    def test_return_type(self):
        assert isinstance(pbm_border_density(_1X1_BLACK), float)

    def test_exact_1_0_for_1x1_black(self):
        assert pbm_border_density(_1X1_BLACK) == 1.0

    def test_exact_0_5_for_2x2_checker(self):
        assert pbm_border_density(_2X2_CHECKER) == 0.5

    def test_between_0_and_1(self):
        d = pbm_border_density(_3X2_PATTERN)
        assert 0.0 <= d <= 1.0

    def test_consistent_across_calls(self):
        assert pbm_border_density(_1X1_BLACK) == pbm_border_density(_1X1_BLACK)


class TestPbmRowBlackVariance:
    def test_return_type(self):
        assert isinstance(pbm_row_black_variance(_1X1_BLACK), float)

    def test_zero_for_1x1_black(self):
        # single pixel = no variance
        assert pbm_row_black_variance(_1X1_BLACK) == 0.0

    def test_zero_for_2x2_checker(self):
        # uniform row counts = no variance
        assert pbm_row_black_variance(_2X2_CHECKER) == 0.0

    def test_positive_for_3x2_pattern(self):
        # rows have different black counts
        assert pbm_row_black_variance(_3X2_PATTERN) == 0.25

    def test_nonnegative(self):
        assert pbm_row_black_variance(_1X1_BLACK) >= 0.0

    def test_consistent_across_calls(self):
        assert pbm_row_black_variance(_3X2_PATTERN) == pbm_row_black_variance(_3X2_PATTERN)
