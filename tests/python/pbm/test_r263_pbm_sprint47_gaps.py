"""Tests for PBM Sprint 47 gap closure.

Closes:
  GAP-PBM-FOSS-PBM_INTERIOR-001  (Pbm Interior Black Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_interior_black_count

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_BLACK_1X1 = str(_DIR / "1x1-black.pbm")
_CHECKER_2X2 = str(_DIR / "2x2-checker.pbm")
_PATTERN_3X2 = str(_DIR / "3x2-pattern.pbm")


class TestPbmInteriorBlackCount:
    def test_return_type(self):
        assert isinstance(pbm_interior_black_count(_BLACK_1X1), int)

    def test_zero_for_1x1(self):
        # 1x1 has no interior pixels
        assert pbm_interior_black_count(_BLACK_1X1) == 0

    def test_zero_for_2x2_checker(self):
        # 2x2 has no interior pixels (all are edge)
        assert pbm_interior_black_count(_CHECKER_2X2) == 0

    def test_zero_for_3x2_pattern(self):
        assert pbm_interior_black_count(_PATTERN_3X2) == 0

    def test_nonnegative(self):
        assert pbm_interior_black_count(_BLACK_1X1) >= 0

    def test_consistent_across_calls(self):
        assert pbm_interior_black_count(_BLACK_1X1) == pbm_interior_black_count(_BLACK_1X1)
