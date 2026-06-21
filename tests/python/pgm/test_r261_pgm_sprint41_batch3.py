"""Tests for PGM Sprint 41 batch 3 gap closure.

Closes:
  GAP-PGM-FOSS-PGM_PIXEL_RA-001  (Pgm Pixel Range)
  GAP-PGM-FOSS-PGM_SHADOW_P-001  (Pgm Shadow Pixel Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import pgm_pixel_range, pgm_shadow_pixel_count

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_1X1_WHITE = str(_DIR / "1x1-white.pgm")
_2X2_GRADIENT = str(_DIR / "2x2-gradient.pgm")


class TestPgmPixelRange:
    def test_return_type(self):
        assert isinstance(pgm_pixel_range(_1X1_WHITE), int)

    def test_zero_for_1x1_white(self):
        assert pgm_pixel_range(_1X1_WHITE) == 0

    def test_exact_255_for_2x2_gradient(self):
        assert pgm_pixel_range(_2X2_GRADIENT) == 255

    def test_nonnegative(self):
        assert pgm_pixel_range(_1X1_WHITE) >= 0

    def test_consistent_across_calls(self):
        assert pgm_pixel_range(_1X1_WHITE) == pgm_pixel_range(_1X1_WHITE)


class TestPgmShadowPixelCount:
    def test_return_type(self):
        assert isinstance(pgm_shadow_pixel_count(_1X1_WHITE), int)

    def test_zero_for_1x1_white(self):
        assert pgm_shadow_pixel_count(_1X1_WHITE) == 0

    def test_exact_2_for_2x2_gradient(self):
        assert pgm_shadow_pixel_count(_2X2_GRADIENT) == 2

    def test_nonnegative(self):
        assert pgm_shadow_pixel_count(_1X1_WHITE) >= 0

    def test_consistent_across_calls(self):
        assert pgm_shadow_pixel_count(_1X1_WHITE) == pgm_shadow_pixel_count(_1X1_WHITE)
