"""Tests for pbm_is_wider_than_tall (Sprint 40 batch 2).

Closes:
  GAP-PBM-FOSS-PBM_IS_WIDER-001  (Pbm Is Wider Than Tall)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_is_wider_than_tall

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_1X1_BLACK = str(_DIR / "1x1-black.pbm")
_2X2_CHECK = str(_DIR / "2x2-checker.pbm")
_3X2_PAT = str(_DIR / "3x2-pattern.pbm")


class TestPbmIsWiderThanTall:
    def test_return_type(self):
        assert isinstance(pbm_is_wider_than_tall(_1X1_BLACK), bool)

    def test_false_for_1x1(self):
        # square -> not wider than tall
        assert pbm_is_wider_than_tall(_1X1_BLACK) is False

    def test_false_for_2x2(self):
        # square
        assert pbm_is_wider_than_tall(_2X2_CHECK) is False

    def test_true_for_3x2(self):
        # 3 wide x 2 tall -> wider
        assert pbm_is_wider_than_tall(_3X2_PAT) is True

    def test_consistent_across_calls(self):
        assert pbm_is_wider_than_tall(_1X1_BLACK) == pbm_is_wider_than_tall(_1X1_BLACK)
