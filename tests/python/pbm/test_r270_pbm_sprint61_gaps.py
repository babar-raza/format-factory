"""Tests for PBM Sprint 61 gap closure (batch 2).

Closes:
  GAP-PBM-FOSS-PBM_WHITE_PE-001   (Pbm White Per Row)
  GAP-PBM-FOSS-PBM_IS_SINGL-001   (Pbm Is Single Row)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_white_per_row, pbm_is_single_row

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_1X1 = str(_DIR / "1x1-black.pbm")
_2X2 = str(_DIR / "2x2-checker.pbm")
_3X2 = str(_DIR / "3x2-pattern.pbm")


class TestPbmWhitePerRow:
    def test_return_type(self):
        assert isinstance(pbm_white_per_row(_1X1), (int, float))

    def test_zero_for_1x1_black(self):
        assert pbm_white_per_row(_1X1) == 0.0

    def test_exact_1_0_for_2x2_checker(self):
        assert pbm_white_per_row(_2X2) == 1.0

    def test_exact_1_5_for_3x2_pattern(self):
        assert pbm_white_per_row(_3X2) == 1.5

    def test_nonnegative(self):
        assert pbm_white_per_row(_1X1) >= 0

    def test_consistent_across_calls(self):
        assert pbm_white_per_row(_1X1) == pbm_white_per_row(_1X1)


class TestPbmIsSingleRow:
    def test_return_type(self):
        assert isinstance(pbm_is_single_row(_1X1), bool)

    def test_true_for_1x1(self):
        assert pbm_is_single_row(_1X1) is True

    def test_false_for_2x2(self):
        assert pbm_is_single_row(_2X2) is False

    def test_false_for_3x2(self):
        assert pbm_is_single_row(_3X2) is False

    def test_consistent_across_calls(self):
        assert pbm_is_single_row(_1X1) == pbm_is_single_row(_1X1)
