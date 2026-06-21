"""Tests for PGM Sprint 52 gap closure.

Closes:
  GAP-PGM-FOSS-PGM_BORDER_M-001   (Pgm Border Mean)
  GAP-PGM-FOSS-PGM_BELOW_AV-001   (Pgm Below Average Count)
  GAP-PGM-FOSS-PGM_FULL_WHI-001   (Pgm Full White Pixel Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import pgm_border_mean, pgm_below_average_count, pgm_full_white_pixel_count

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_WHITE = str(_DIR / "1x1-white.pgm")
_GRAD = str(_DIR / "2x2-gradient.pgm")
_RAMP = str(_DIR / "3x1-ramp.pgm")


class TestPgmBorderMean:
    def test_return_type(self):
        assert isinstance(pgm_border_mean(_WHITE), (int, float))

    def test_exact_255_for_white(self):
        assert pgm_border_mean(_WHITE) == 255.0

    def test_exact_127_5_for_gradient(self):
        assert pgm_border_mean(_GRAD) == 127.5

    def test_positive(self):
        assert pgm_border_mean(_WHITE) > 0

    def test_consistent_across_calls(self):
        assert pgm_border_mean(_WHITE) == pgm_border_mean(_WHITE)


class TestPgmBelowAverageCount:
    def test_return_type(self):
        assert isinstance(pgm_below_average_count(_WHITE), int)

    def test_zero_for_white(self):
        assert pgm_below_average_count(_WHITE) == 0

    def test_exact_2_for_gradient(self):
        assert pgm_below_average_count(_GRAD) == 2

    def test_exact_1_for_ramp(self):
        assert pgm_below_average_count(_RAMP) == 1

    def test_nonnegative(self):
        assert pgm_below_average_count(_WHITE) >= 0

    def test_consistent_across_calls(self):
        assert pgm_below_average_count(_WHITE) == pgm_below_average_count(_WHITE)


class TestPgmFullWhitePixelCount:
    def test_return_type(self):
        assert isinstance(pgm_full_white_pixel_count(_WHITE), int)

    def test_exact_1_for_white(self):
        assert pgm_full_white_pixel_count(_WHITE) == 1

    def test_exact_1_for_gradient(self):
        assert pgm_full_white_pixel_count(_GRAD) == 1

    def test_exact_1_for_ramp(self):
        assert pgm_full_white_pixel_count(_RAMP) == 1

    def test_nonnegative(self):
        assert pgm_full_white_pixel_count(_WHITE) >= 0

    def test_consistent_across_calls(self):
        assert pgm_full_white_pixel_count(_WHITE) == pgm_full_white_pixel_count(_WHITE)
