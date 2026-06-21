"""Tests for PGM Sprint 41 gap closure.

Closes:
  GAP-PGM-FOSS-PGM_ENTROPY_-001  (Pgm Entropy)
  GAP-PGM-FOSS-PGM_MODE_PIX-001  (Pgm Mode Pixel Value)
  GAP-PGM-FOSS-PGM_MIDTONE_-001  (Pgm Midtone Pixel Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import pgm_entropy, pgm_midtone_pixel_count, pgm_mode_pixel_value

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_1X1_WHITE = str(_DIR / "1x1-white.pgm")
_2X2_GRADIENT = str(_DIR / "2x2-gradient.pgm")


class TestPgmEntropy:
    def test_return_type(self):
        assert isinstance(pgm_entropy(_1X1_WHITE), float)

    def test_exact_0_0_for_1x1_white(self):
        assert pgm_entropy(_1X1_WHITE) == 0.0

    def test_exact_2_0_for_2x2_gradient(self):
        assert pgm_entropy(_2X2_GRADIENT) == 2.0

    def test_nonnegative(self):
        assert pgm_entropy(_1X1_WHITE) >= 0.0

    def test_consistent_across_calls(self):
        assert pgm_entropy(_1X1_WHITE) == pgm_entropy(_1X1_WHITE)


class TestPgmModePixelValue:
    def test_return_type(self):
        assert isinstance(pgm_mode_pixel_value(_1X1_WHITE), int)

    def test_exact_255_for_1x1_white(self):
        assert pgm_mode_pixel_value(_1X1_WHITE) == 255

    def test_exact_0_for_2x2_gradient(self):
        assert pgm_mode_pixel_value(_2X2_GRADIENT) == 0

    def test_nonnegative(self):
        assert pgm_mode_pixel_value(_1X1_WHITE) >= 0

    def test_consistent_across_calls(self):
        assert pgm_mode_pixel_value(_1X1_WHITE) == pgm_mode_pixel_value(_1X1_WHITE)


class TestPgmMidtonePixelCount:
    def test_return_type(self):
        assert isinstance(pgm_midtone_pixel_count(_1X1_WHITE), int)

    def test_zero_for_1x1_white(self):
        assert pgm_midtone_pixel_count(_1X1_WHITE) == 0

    def test_exact_2_for_2x2_gradient(self):
        assert pgm_midtone_pixel_count(_2X2_GRADIENT) == 2

    def test_nonnegative(self):
        assert pgm_midtone_pixel_count(_1X1_WHITE) >= 0

    def test_consistent_across_calls(self):
        assert pgm_midtone_pixel_count(_1X1_WHITE) == pgm_midtone_pixel_count(_1X1_WHITE)
