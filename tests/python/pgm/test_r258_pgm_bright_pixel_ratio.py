"""Tests for pgm_bright_pixel_ratio (Sprint 40 batch 3).

Closes:
  GAP-PGM-FOSS-PGM_BRIGHT_P-001  (Pgm Bright Pixel Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import pgm_bright_pixel_ratio

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_1X1_WHITE = str(_DIR / "1x1-white.pgm")
_2X2_GRADIENT = str(_DIR / "2x2-gradient.pgm")
_3X1_RAMP = str(_DIR / "3x1-ramp.pgm")


class TestPgmBrightPixelRatio:
    def test_return_type(self):
        assert isinstance(pgm_bright_pixel_ratio(_1X1_WHITE), float)

    def test_exact_1_0_for_1x1_white(self):
        # single white pixel = ratio 1.0
        assert pgm_bright_pixel_ratio(_1X1_WHITE) == 1.0

    def test_exact_0_25_for_2x2_gradient(self):
        # threshold=192; only pixel 255 is bright → 1/4 = 0.25
        assert pgm_bright_pixel_ratio(_2X2_GRADIENT) == 0.25

    def test_between_0_and_1(self):
        r = pgm_bright_pixel_ratio(_3X1_RAMP)
        assert 0.0 <= r <= 1.0

    def test_nonnegative(self):
        assert pgm_bright_pixel_ratio(_1X1_WHITE) >= 0.0

    def test_consistent_across_calls(self):
        assert pgm_bright_pixel_ratio(_1X1_WHITE) == pgm_bright_pixel_ratio(_1X1_WHITE)
