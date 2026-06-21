"""Tests for PBM Sprint 61 gap closure (batch 3).

Closes:
  GAP-PBM-FOSS-PBM_BORDER_W-001   (Pbm Border White Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_border_white_count

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_1X1 = str(_DIR / "1x1-black.pbm")
_2X2 = str(_DIR / "2x2-checker.pbm")
_3X2 = str(_DIR / "3x2-pattern.pbm")


class TestPbmBorderWhiteCount:
    def test_return_type(self):
        assert isinstance(pbm_border_white_count(_1X1), int)

    def test_zero_for_1x1_black(self):
        assert pbm_border_white_count(_1X1) == 0

    def test_exact_2_for_2x2_checker(self):
        assert pbm_border_white_count(_2X2) == 2

    def test_exact_3_for_3x2_pattern(self):
        assert pbm_border_white_count(_3X2) == 3

    def test_nonnegative(self):
        assert pbm_border_white_count(_1X1) >= 0

    def test_consistent_across_calls(self):
        assert pbm_border_white_count(_1X1) == pbm_border_white_count(_1X1)
