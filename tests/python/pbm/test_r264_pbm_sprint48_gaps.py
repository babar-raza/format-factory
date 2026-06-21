"""Tests for PBM Sprint 48 gap closure.

Closes:
  GAP-PBM-FOSS-PBM_BLACK_CO-001  (Pbm Black Column Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_black_column_count

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_BLACK_1X1 = str(_DIR / "1x1-black.pbm")
_CHECKER_2X2 = str(_DIR / "2x2-checker.pbm")
_PATTERN_3X2 = str(_DIR / "3x2-pattern.pbm")


class TestPbmBlackColumnCount:
    def test_return_type(self):
        assert isinstance(pbm_black_column_count(_BLACK_1X1), int)

    def test_exact_1_for_1x1_black(self):
        assert pbm_black_column_count(_BLACK_1X1) == 1

    def test_exact_2_for_2x2_checker(self):
        assert pbm_black_column_count(_CHECKER_2X2) == 2

    def test_exact_3_for_3x2_pattern(self):
        assert pbm_black_column_count(_PATTERN_3X2) == 3

    def test_positive(self):
        assert pbm_black_column_count(_BLACK_1X1) > 0

    def test_consistent_across_calls(self):
        assert pbm_black_column_count(_BLACK_1X1) == pbm_black_column_count(_BLACK_1X1)
