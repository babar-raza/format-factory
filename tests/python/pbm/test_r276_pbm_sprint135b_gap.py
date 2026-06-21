"""Tests for PBM Sprint 135b gap closure.

Closes:
  GAP-PBM-FOSS-PBM_WHITE_CO-001   (Pbm White Count Exceeds Row Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_white_count_exceeds_row_count

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_BLACK = str(_DIR / "1x1-black.pbm")
_CHECKER = str(_DIR / "2x2-checker.pbm")
_PATTERN = str(_DIR / "3x2-pattern.pbm")


class TestPbmWhiteCountExceedsRowCount:
    def test_return_type(self):
        assert isinstance(pbm_white_count_exceeds_row_count(_BLACK), bool)

    def test_false_for_1x1_black(self):
        assert pbm_white_count_exceeds_row_count(_BLACK) is False

    def test_false_for_2x2_checker(self):
        assert pbm_white_count_exceeds_row_count(_CHECKER) is False

    def test_true_for_3x2_pattern(self):
        assert pbm_white_count_exceeds_row_count(_PATTERN) is True

    def test_is_bool(self):
        assert type(pbm_white_count_exceeds_row_count(_BLACK)) is bool

    def test_consistent(self):
        assert pbm_white_count_exceeds_row_count(_BLACK) == pbm_white_count_exceeds_row_count(_BLACK)
