"""Tests for PBM Sprint 45 gap closure.

Closes:
  GAP-PBM-FOSS-PBM_BLACK_EX-001  (Pbm Black Exceeds White)
  GAP-PBM-FOSS-PBM_EDGE_PIX-001  (Pbm Edge Pixel Sum)
  GAP-PBM-FOSS-PBM_CENTER_P-001  (Pbm Center Pixel Value)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_black_exceeds_white, pbm_edge_pixel_sum, pbm_center_pixel_value

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_BLACK_1X1 = str(_DIR / "1x1-black.pbm")
_CHECKER_2X2 = str(_DIR / "2x2-checker.pbm")
_PATTERN_3X2 = str(_DIR / "3x2-pattern.pbm")


class TestPbmBlackExceedsWhite:
    def test_return_type(self):
        assert isinstance(pbm_black_exceeds_white(_BLACK_1X1), bool)

    def test_true_for_all_black_1x1(self):
        assert pbm_black_exceeds_white(_BLACK_1X1) is True

    def test_false_for_checker_equal_counts(self):
        assert pbm_black_exceeds_white(_CHECKER_2X2) is False

    def test_false_for_pattern_3x2(self):
        assert pbm_black_exceeds_white(_PATTERN_3X2) is False

    def test_consistent_across_calls(self):
        assert pbm_black_exceeds_white(_BLACK_1X1) == pbm_black_exceeds_white(_BLACK_1X1)


class TestPbmEdgePixelSum:
    def test_return_type(self):
        assert isinstance(pbm_edge_pixel_sum(_BLACK_1X1), int)

    def test_exact_1_for_1x1_black(self):
        assert pbm_edge_pixel_sum(_BLACK_1X1) == 1

    def test_exact_2_for_2x2_checker(self):
        assert pbm_edge_pixel_sum(_CHECKER_2X2) == 2

    def test_nonnegative(self):
        assert pbm_edge_pixel_sum(_BLACK_1X1) >= 0

    def test_consistent_across_calls(self):
        assert pbm_edge_pixel_sum(_BLACK_1X1) == pbm_edge_pixel_sum(_BLACK_1X1)


class TestPbmCenterPixelValue:
    def test_return_type(self):
        assert isinstance(pbm_center_pixel_value(_BLACK_1X1), int)

    def test_exact_1_for_1x1_black(self):
        assert pbm_center_pixel_value(_BLACK_1X1) == 1

    def test_exact_1_for_2x2_checker(self):
        assert pbm_center_pixel_value(_CHECKER_2X2) == 1

    def test_binary_value(self):
        assert pbm_center_pixel_value(_BLACK_1X1) in (0, 1)

    def test_consistent_across_calls(self):
        assert pbm_center_pixel_value(_BLACK_1X1) == pbm_center_pixel_value(_BLACK_1X1)
