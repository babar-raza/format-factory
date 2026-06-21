"""Tests for PBM Sprint 56 gap closure.

Closes:
  GAP-PBM-FOSS-PBM_HEIGHT-001  (Pbm Height)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_height

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_BLACK = str(_DIR / "1x1-black.pbm")
_CHECKER = str(_DIR / "2x2-checker.pbm")
_PATTERN = str(_DIR / "3x2-pattern.pbm")


class TestPbmHeight:
    def test_return_type(self):
        assert isinstance(pbm_height(_BLACK), int)

    def test_exact_1_for_1x1(self):
        assert pbm_height(_BLACK) == 1

    def test_exact_2_for_2x2(self):
        assert pbm_height(_CHECKER) == 2

    def test_exact_2_for_3x2(self):
        assert pbm_height(_PATTERN) == 2

    def test_positive(self):
        assert pbm_height(_BLACK) > 0

    def test_consistent_across_calls(self):
        assert pbm_height(_BLACK) == pbm_height(_BLACK)
