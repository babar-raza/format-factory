"""Tests for PBM Sprint 51 gap closure.

Closes:
  GAP-PBM-FOSS-PBM_MIN_COL_-001  (Pbm Min Col Black Count)
  GAP-PBM-FOSS-PBM_TOTAL_WH-001  (Pbm Total White Pixels)
  GAP-PBM-FOSS-PBM_BLACK_WH-001  (Pbm Black White Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_min_col_black_count, pbm_total_white_pixels, pbm_black_white_ratio

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_BLACK = str(_DIR / "1x1-black.pbm")
_CHECKER = str(_DIR / "2x2-checker.pbm")
_PATTERN = str(_DIR / "3x2-pattern.pbm")


class TestPbmMinColBlackCount:
    def test_return_type(self):
        assert isinstance(pbm_min_col_black_count(_BLACK), int)

    def test_exact_1_for_black(self):
        assert pbm_min_col_black_count(_BLACK) == 1

    def test_exact_1_for_checker(self):
        assert pbm_min_col_black_count(_CHECKER) == 1

    def test_exact_1_for_pattern(self):
        assert pbm_min_col_black_count(_PATTERN) == 1

    def test_nonnegative(self):
        assert pbm_min_col_black_count(_BLACK) >= 0

    def test_consistent_across_calls(self):
        assert pbm_min_col_black_count(_BLACK) == pbm_min_col_black_count(_BLACK)


class TestPbmTotalWhitePixels:
    def test_return_type(self):
        assert isinstance(pbm_total_white_pixels(_BLACK), int)

    def test_zero_for_black(self):
        assert pbm_total_white_pixels(_BLACK) == 0

    def test_exact_2_for_checker(self):
        assert pbm_total_white_pixels(_CHECKER) == 2

    def test_exact_3_for_pattern(self):
        assert pbm_total_white_pixels(_PATTERN) == 3

    def test_nonnegative(self):
        assert pbm_total_white_pixels(_BLACK) >= 0

    def test_consistent_across_calls(self):
        assert pbm_total_white_pixels(_BLACK) == pbm_total_white_pixels(_BLACK)


class TestPbmBlackWhiteRatio:
    def test_return_type(self):
        assert isinstance(pbm_black_white_ratio(_CHECKER), (int, float))

    def test_zero_for_all_black(self):
        assert pbm_black_white_ratio(_BLACK) == 0.0

    def test_exact_1_for_checker(self):
        assert pbm_black_white_ratio(_CHECKER) == 1.0

    def test_exact_1_for_pattern(self):
        assert pbm_black_white_ratio(_PATTERN) == 1.0

    def test_nonnegative(self):
        assert pbm_black_white_ratio(_CHECKER) >= 0

    def test_consistent_across_calls(self):
        assert pbm_black_white_ratio(_CHECKER) == pbm_black_white_ratio(_CHECKER)
