"""Tests for PGM Sprint 56 gap closure.

Closes:
  GAP-PGM-FOSS-PGM_HEIGHT-001  (Pgm Height)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import pgm_height

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_WHITE = str(_DIR / "1x1-white.pgm")
_GRAD = str(_DIR / "2x2-gradient.pgm")
_RAMP = str(_DIR / "3x1-ramp.pgm")


class TestPgmHeight:
    def test_return_type(self):
        assert isinstance(pgm_height(_WHITE), int)

    def test_exact_1_for_1x1(self):
        assert pgm_height(_WHITE) == 1

    def test_exact_2_for_2x2(self):
        assert pgm_height(_GRAD) == 2

    def test_exact_1_for_3x1(self):
        assert pgm_height(_RAMP) == 1

    def test_positive(self):
        assert pgm_height(_WHITE) > 0

    def test_consistent_across_calls(self):
        assert pgm_height(_WHITE) == pgm_height(_WHITE)
