"""Tests for PGM product deepening sprint 151.

New functions:
  pgm_maxval_times_pixel_count — maxval multiplied by total pixel count
  pgm_pixel_sum_minus_count    — sum of pixel values minus number of pixels
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pgm import pgm_maxval_times_pixel_count, pgm_pixel_sum_minus_count

_WHITE = str(_REPO / "samples" / "by-format" / "pgm" / "valid" / "1x1-white.pgm")
_GRAD = str(_REPO / "samples" / "by-format" / "pgm" / "valid" / "2x2-gradient.pgm")
_RAMP = str(_REPO / "samples" / "by-format" / "pgm" / "valid" / "3x1-ramp.pgm")


class TestPgmMaxvalTimesPixelCount:
    def test_return_type(self):
        assert isinstance(pgm_maxval_times_pixel_count(_WHITE), int)

    def test_exact_255_for_white(self):
        # 1x1-white.pgm: maxval=255, pixels=1 → 255
        assert pgm_maxval_times_pixel_count(_WHITE) == 255

    def test_exact_1020_for_gradient(self):
        # 2x2-gradient.pgm: maxval=255, pixels=4 → 1020
        assert pgm_maxval_times_pixel_count(_GRAD) == 1020

    def test_exact_765_for_ramp(self):
        # 3x1-ramp.pgm: maxval=255, pixels=3 → 765
        assert pgm_maxval_times_pixel_count(_RAMP) == 765

    def test_positive(self):
        assert pgm_maxval_times_pixel_count(_WHITE) > 0

    def test_consistent(self):
        assert pgm_maxval_times_pixel_count(_GRAD) == pgm_maxval_times_pixel_count(_GRAD)


class TestPgmPixelSumMinusCount:
    def test_return_type(self):
        assert isinstance(pgm_pixel_sum_minus_count(_WHITE), int)

    def test_exact_254_for_white(self):
        # 1x1-white.pgm: sum=255, count=1 → 254
        assert pgm_pixel_sum_minus_count(_WHITE) == 254

    def test_exact_506_for_gradient(self):
        # 2x2-gradient.pgm: sum=510, count=4 → 506
        assert pgm_pixel_sum_minus_count(_GRAD) == 506

    def test_exact_380_for_ramp(self):
        # 3x1-ramp.pgm: sum=383, count=3 → 380
        assert pgm_pixel_sum_minus_count(_RAMP) == 380

    def test_nonnegative(self):
        assert pgm_pixel_sum_minus_count(_WHITE) >= 0

    def test_consistent(self):
        assert pgm_pixel_sum_minus_count(_RAMP) == pgm_pixel_sum_minus_count(_RAMP)
