"""Tests for PBM Sprint 74 gap closure.

Closes:
  GAP-PBM-FOSS-PBM_ROW_TRAN-001   (Pbm Row Transition Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_row_transition_count

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_BLACK = str(_DIR / "1x1-black.pbm")
_CHECKER = str(_DIR / "2x2-checker.pbm")
_PATTERN = str(_DIR / "3x2-pattern.pbm")


class TestPbmRowTransitionCount:
    def test_return_type(self):
        assert isinstance(pbm_row_transition_count(_BLACK), int)

    def test_zero_for_1x1_black(self):
        assert pbm_row_transition_count(_BLACK) == 0

    def test_exact_2_for_checker(self):
        assert pbm_row_transition_count(_CHECKER) == 2

    def test_exact_4_for_pattern(self):
        assert pbm_row_transition_count(_PATTERN) == 4

    def test_nonnegative(self):
        assert pbm_row_transition_count(_BLACK) >= 0

    def test_consistent_across_calls(self):
        assert pbm_row_transition_count(_BLACK) == pbm_row_transition_count(_BLACK)
