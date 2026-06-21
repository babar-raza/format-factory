"""Tests for PGM Sprint 47 gap closure.

Closes:
  GAP-PGM-FOSS-PGM_ROW_MEAN-001   (Pgm Row Mean)
  GAP-PGM-FOSS-PGM_PIXEL_QU-001   (Pgm Pixel Quartile Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import pgm_row_mean, pgm_pixel_quartile_count

_DIR = _REPO / "samples" / "by-format" / "pgm" / "valid"
_WHITE_1X1 = str(_DIR / "1x1-white.pgm")
_GRADIENT_2X2 = str(_DIR / "2x2-gradient.pgm")
_RAMP_3X1 = str(_DIR / "3x1-ramp.pgm")


class TestPgmRowMean:
    def test_return_type(self):
        assert isinstance(pgm_row_mean(_WHITE_1X1), (int, float))

    def test_exact_255_for_1x1_white(self):
        assert pgm_row_mean(_WHITE_1X1) == 255.0

    def test_exact_127_5_for_gradient(self):
        assert pgm_row_mean(_GRADIENT_2X2) == 127.5

    def test_in_valid_range(self):
        assert 0 <= pgm_row_mean(_WHITE_1X1) <= 255

    def test_consistent_across_calls(self):
        assert pgm_row_mean(_WHITE_1X1) == pgm_row_mean(_WHITE_1X1)


class TestPgmPixelQuartileCount:
    def test_return_type(self):
        assert isinstance(pgm_pixel_quartile_count(_WHITE_1X1), int)

    def test_exact_1_for_1x1_white(self):
        assert pgm_pixel_quartile_count(_WHITE_1X1) == 1

    def test_exact_4_for_gradient_2x2(self):
        assert pgm_pixel_quartile_count(_GRADIENT_2X2) == 4

    def test_exact_3_for_ramp_3x1(self):
        assert pgm_pixel_quartile_count(_RAMP_3X1) == 3

    def test_positive(self):
        assert pgm_pixel_quartile_count(_WHITE_1X1) > 0

    def test_consistent_across_calls(self):
        assert pgm_pixel_quartile_count(_WHITE_1X1) == pgm_pixel_quartile_count(_WHITE_1X1)
