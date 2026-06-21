"""Tests for PGM Sprint 63 gap closure.

Closes:
  GAP-PGM-FOSS-PGM_IS_MULTI-001   (Pgm Is Multi Row)
  GAP-PGM-FOSS-PGM_MAXVAL_E-001   (Pgm Maxval Exceeds Avg)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import pgm_is_multi_row, pgm_maxval_exceeds_avg

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_1X1 = str(_DIR / "1x1-white.pgm")
_2X2 = str(_DIR / "2x2-gradient.pgm")
_3X1 = str(_DIR / "3x1-ramp.pgm")


class TestPgmIsMultiRow:
    def test_return_type(self):
        assert isinstance(pgm_is_multi_row(_1X1), bool)

    def test_false_for_1x1(self):
        assert pgm_is_multi_row(_1X1) is False

    def test_true_for_2x2(self):
        assert pgm_is_multi_row(_2X2) is True

    def test_false_for_3x1(self):
        assert pgm_is_multi_row(_3X1) is False

    def test_consistent_across_calls(self):
        assert pgm_is_multi_row(_1X1) == pgm_is_multi_row(_1X1)


class TestPgmMaxvalExceedsAvg:
    def test_return_type(self):
        assert isinstance(pgm_maxval_exceeds_avg(_1X1), bool)

    def test_false_for_1x1_white(self):
        assert pgm_maxval_exceeds_avg(_1X1) is False

    def test_true_for_2x2_gradient(self):
        assert pgm_maxval_exceeds_avg(_2X2) is True

    def test_true_for_3x1_ramp(self):
        assert pgm_maxval_exceeds_avg(_3X1) is True

    def test_consistent_across_calls(self):
        assert pgm_maxval_exceeds_avg(_1X1) == pgm_maxval_exceeds_avg(_1X1)
