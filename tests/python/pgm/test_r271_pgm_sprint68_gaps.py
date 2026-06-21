"""Tests for PGM Sprint 68 gap closure.

Closes:
  GAP-PGM-FOSS-PGM_CENTER_P-001   (Pgm Center Pixel Value)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import pgm_center_pixel_value

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_WHITE = str(_DIR / "1x1-white.pgm")
_GRAD = str(_DIR / "2x2-gradient.pgm")
_RAMP = str(_DIR / "3x1-ramp.pgm")


class TestPgmCenterPixelValue:
    def test_return_type(self):
        assert isinstance(pgm_center_pixel_value(_WHITE), (int, float))

    def test_exact_255_for_1x1_white(self):
        assert pgm_center_pixel_value(_WHITE) == 255

    def test_exact_255_for_2x2_gradient(self):
        assert pgm_center_pixel_value(_GRAD) == 255

    def test_exact_128_for_3x1_ramp(self):
        assert pgm_center_pixel_value(_RAMP) == 128

    def test_nonnegative(self):
        assert pgm_center_pixel_value(_WHITE) >= 0

    def test_consistent_across_calls(self):
        assert pgm_center_pixel_value(_WHITE) == pgm_center_pixel_value(_WHITE)
