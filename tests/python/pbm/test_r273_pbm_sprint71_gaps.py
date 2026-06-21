"""Tests for PBM Sprint 71 gap closure.

Closes:
  GAP-PBM-FOSS-PBM_COL_BLAC-001   (Pbm Col Black Variance)
  GAP-PBM-FOSS-PBM_LONGEST_-001   (Pbm Longest Run)
  GAP-PBM-FOSS-PBM_TOP_HALF-001   (Pbm Top Half Density)
  GAP-PBM-FOSS-PBM_BOTTOM_H-001   (Pbm Bottom Half Density)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_col_black_variance, pbm_longest_run, pbm_top_half_density, pbm_bottom_half_density

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_BLACK = str(_DIR / "1x1-black.pbm")
_CHECKER = str(_DIR / "2x2-checker.pbm")
_PATTERN = str(_DIR / "3x2-pattern.pbm")


class TestPbmColBlackVariance:
    def test_return_type(self):
        assert isinstance(pbm_col_black_variance(_BLACK), (int, float))

    def test_zero_for_1x1_black(self):
        assert pbm_col_black_variance(_BLACK) == 0.0

    def test_zero_for_checker(self):
        assert pbm_col_black_variance(_CHECKER) == 0.0

    def test_zero_for_pattern(self):
        assert pbm_col_black_variance(_PATTERN) == 0.0

    def test_nonnegative(self):
        assert pbm_col_black_variance(_BLACK) >= 0.0

    def test_consistent_across_calls(self):
        assert pbm_col_black_variance(_BLACK) == pbm_col_black_variance(_BLACK)


class TestPbmLongestRun:
    def test_return_type(self):
        assert isinstance(pbm_longest_run(_BLACK), int)

    def test_exact_1_for_1x1_black(self):
        assert pbm_longest_run(_BLACK) == 1

    def test_exact_1_for_checker(self):
        assert pbm_longest_run(_CHECKER) == 1

    def test_exact_1_for_pattern(self):
        assert pbm_longest_run(_PATTERN) == 1

    def test_positive(self):
        assert pbm_longest_run(_BLACK) > 0

    def test_consistent_across_calls(self):
        assert pbm_longest_run(_BLACK) == pbm_longest_run(_BLACK)


class TestPbmTopHalfDensity:
    def test_return_type(self):
        assert isinstance(pbm_top_half_density(_BLACK), (int, float))

    def test_exact_1_0_for_1x1_black(self):
        assert pbm_top_half_density(_BLACK) == 1.0

    def test_exact_0_5_for_checker(self):
        assert pbm_top_half_density(_CHECKER) == 0.5

    def test_approx_0_667_for_pattern(self):
        assert pbm_top_half_density(_PATTERN) == pytest.approx(0.6667, rel=1e-2)

    def test_between_0_and_1(self):
        assert 0.0 <= pbm_top_half_density(_CHECKER) <= 1.0

    def test_consistent_across_calls(self):
        assert pbm_top_half_density(_BLACK) == pbm_top_half_density(_BLACK)


class TestPbmBottomHalfDensity:
    def test_return_type(self):
        assert isinstance(pbm_bottom_half_density(_BLACK), (int, float))

    def test_zero_for_1x1_black(self):
        assert pbm_bottom_half_density(_BLACK) == 0.0

    def test_exact_0_5_for_checker(self):
        assert pbm_bottom_half_density(_CHECKER) == 0.5

    def test_approx_0_333_for_pattern(self):
        assert pbm_bottom_half_density(_PATTERN) == pytest.approx(0.3333, rel=1e-2)

    def test_between_0_and_1(self):
        assert 0.0 <= pbm_bottom_half_density(_CHECKER) <= 1.0

    def test_consistent_across_calls(self):
        assert pbm_bottom_half_density(_BLACK) == pbm_bottom_half_density(_BLACK)
