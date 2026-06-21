"""Tests for PBM Sprint 41 gap closure.

Closes:
  GAP-PBM-FOSS-PBM_CORNER_B-001  (Pbm Corner Black Count)
  GAP-PBM-FOSS-PBM_ROW_UNIF-001  (Pbm Row Uniformity)
  GAP-PBM-FOSS-PBM_WHITE_RO-001  (Pbm White Row Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_corner_black_count, pbm_row_uniformity, pbm_white_row_count

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_1X1_BLACK = str(_DIR / "1x1-black.pbm")
_2X2_CHECKER = str(_DIR / "2x2-checker.pbm")
_3X2_PATTERN = str(_DIR / "3x2-pattern.pbm")


class TestPbmCornerBlackCount:
    def test_return_type(self):
        assert isinstance(pbm_corner_black_count(_1X1_BLACK), int)

    def test_exact_4_for_1x1_black(self):
        assert pbm_corner_black_count(_1X1_BLACK) == 4

    def test_exact_2_for_2x2_checker(self):
        assert pbm_corner_black_count(_2X2_CHECKER) == 2

    def test_nonnegative(self):
        assert pbm_corner_black_count(_1X1_BLACK) >= 0

    def test_consistent_across_calls(self):
        assert pbm_corner_black_count(_1X1_BLACK) == pbm_corner_black_count(_1X1_BLACK)


class TestPbmRowUniformity:
    def test_return_type(self):
        assert isinstance(pbm_row_uniformity(_1X1_BLACK), float)

    def test_exact_1_0_for_1x1_black(self):
        assert pbm_row_uniformity(_1X1_BLACK) == 1.0

    def test_exact_0_0_for_2x2_checker(self):
        assert pbm_row_uniformity(_2X2_CHECKER) == 0.0

    def test_nonnegative(self):
        assert pbm_row_uniformity(_1X1_BLACK) >= 0.0

    def test_consistent_across_calls(self):
        assert pbm_row_uniformity(_1X1_BLACK) == pbm_row_uniformity(_1X1_BLACK)


class TestPbmWhiteRowCount:
    def test_return_type(self):
        assert isinstance(pbm_white_row_count(_1X1_BLACK), int)

    def test_zero_for_1x1_black(self):
        assert pbm_white_row_count(_1X1_BLACK) == 0

    def test_nonnegative(self):
        assert pbm_white_row_count(_1X1_BLACK) >= 0

    def test_consistent_across_calls(self):
        assert pbm_white_row_count(_1X1_BLACK) == pbm_white_row_count(_1X1_BLACK)
