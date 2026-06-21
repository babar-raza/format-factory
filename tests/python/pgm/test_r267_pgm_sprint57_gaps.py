"""Tests for PGM Sprint 57 gap closure.

Closes:
  GAP-PGM-FOSS-PGM_TOP_ROW_-001   (Pgm Top Row Mean)
  GAP-PGM-FOSS-PGM_BOTTOM_R-001   (Pgm Bottom Row Mean)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import pgm_top_row_mean, pgm_bottom_row_mean

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_1X1 = str(_DIR / "1x1-white.pgm")
_2X2 = str(_DIR / "2x2-gradient.pgm")
_3X1 = str(_DIR / "3x1-ramp.pgm")


class TestPgmTopRowMean:
    def test_return_type(self):
        assert isinstance(pgm_top_row_mean(_1X1), (int, float))

    def test_exact_255_for_1x1_white(self):
        assert pgm_top_row_mean(_1X1) == 255.0

    def test_exact_42_5_for_2x2_gradient(self):
        assert pgm_top_row_mean(_2X2) == 42.5

    def test_approx_127_67_for_3x1_ramp(self):
        assert pgm_top_row_mean(_3X1) == pytest.approx(127.667, rel=1e-3)

    def test_nonnegative(self):
        assert pgm_top_row_mean(_1X1) >= 0

    def test_consistent_across_calls(self):
        assert pgm_top_row_mean(_1X1) == pgm_top_row_mean(_1X1)


class TestPgmBottomRowMean:
    def test_return_type(self):
        assert isinstance(pgm_bottom_row_mean(_1X1), (int, float))

    def test_exact_255_for_1x1_white(self):
        assert pgm_bottom_row_mean(_1X1) == 255.0

    def test_exact_212_5_for_2x2_gradient(self):
        assert pgm_bottom_row_mean(_2X2) == 212.5

    def test_approx_127_67_for_3x1_ramp(self):
        assert pgm_bottom_row_mean(_3X1) == pytest.approx(127.667, rel=1e-3)

    def test_nonnegative(self):
        assert pgm_bottom_row_mean(_1X1) >= 0

    def test_consistent_across_calls(self):
        assert pgm_bottom_row_mean(_1X1) == pgm_bottom_row_mean(_1X1)
