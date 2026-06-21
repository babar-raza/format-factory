"""Tests for PGM Sprint 48 gap closure.

Closes:
  GAP-PGM-FOSS-PGM_ABOVE_AV-001  (Pgm Above Average Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import pgm_above_average_count

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_WHITE_1X1 = str(_DIR / "1x1-white.pgm")
_GRADIENT_2X2 = str(_DIR / "2x2-gradient.pgm")
_RAMP_3X1 = str(_DIR / "3x1-ramp.pgm")


class TestPgmAboveAverageCount:
    def test_return_type(self):
        assert isinstance(pgm_above_average_count(_WHITE_1X1), int)

    def test_zero_for_1x1_white_uniform(self):
        assert pgm_above_average_count(_WHITE_1X1) == 0

    def test_exact_2_for_gradient(self):
        assert pgm_above_average_count(_GRADIENT_2X2) == 2

    def test_exact_2_for_ramp(self):
        assert pgm_above_average_count(_RAMP_3X1) == 2

    def test_nonnegative(self):
        assert pgm_above_average_count(_WHITE_1X1) >= 0

    def test_consistent_across_calls(self):
        assert pgm_above_average_count(_WHITE_1X1) == pgm_above_average_count(_WHITE_1X1)
