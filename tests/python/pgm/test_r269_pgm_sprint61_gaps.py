"""Tests for PGM Sprint 61 gap closure (batch 2).

Closes:
  GAP-PGM-FOSS-PGM_LEFT_COL-001   (Pgm Left Column Mean)
  GAP-PGM-FOSS-PGM_RIGHT_CO-001   (Pgm Right Column Mean)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import pgm_left_column_mean, pgm_right_column_mean

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_1X1 = str(_DIR / "1x1-white.pgm")
_2X2 = str(_DIR / "2x2-gradient.pgm")
_3X1 = str(_DIR / "3x1-ramp.pgm")


class TestPgmLeftColumnMean:
    def test_return_type(self):
        assert isinstance(pgm_left_column_mean(_1X1), (int, float))

    def test_exact_255_for_1x1(self):
        assert pgm_left_column_mean(_1X1) == 255.0

    def test_exact_85_for_2x2(self):
        assert pgm_left_column_mean(_2X2) == 85.0

    def test_exact_0_for_3x1(self):
        assert pgm_left_column_mean(_3X1) == 0.0

    def test_nonnegative(self):
        assert pgm_left_column_mean(_1X1) >= 0

    def test_consistent_across_calls(self):
        assert pgm_left_column_mean(_1X1) == pgm_left_column_mean(_1X1)


class TestPgmRightColumnMean:
    def test_return_type(self):
        assert isinstance(pgm_right_column_mean(_1X1), (int, float))

    def test_exact_255_for_1x1(self):
        assert pgm_right_column_mean(_1X1) == 255.0

    def test_exact_170_for_2x2(self):
        assert pgm_right_column_mean(_2X2) == 170.0

    def test_exact_255_for_3x1(self):
        assert pgm_right_column_mean(_3X1) == 255.0

    def test_nonnegative(self):
        assert pgm_right_column_mean(_1X1) >= 0

    def test_consistent_across_calls(self):
        assert pgm_right_column_mean(_1X1) == pgm_right_column_mean(_1X1)
