"""Tests for pgm_above_average_count and pgm_total_pixel_sum (Sprint r296)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_parser import pgm_above_average_count, pgm_total_pixel_sum

_PGM = _REPO / "samples" / "by-format" / "pgm" / "valid"


class TestPgmAboveAverageCount:
    """Tests for pgm_above_average_count."""

    def test_1x1_white_has_zero_above_average(self):
        """1x1-white.pgm: only pixel is 255 = mean, so 0 pixels above mean."""
        result = pgm_above_average_count(_PGM / "1x1-white.pgm")
        assert result == 0

    def test_2x2_gradient_has_two_above_average(self):
        """2x2-gradient.pgm: pixels [0,85,170,255], mean=127.5 → 2 above."""
        result = pgm_above_average_count(_PGM / "2x2-gradient.pgm")
        assert result == 2

    def test_3x1_ramp_has_two_above_average(self):
        """3x1-ramp.pgm: pixels [0,128,255], mean≈127.67 → 2 above (128 and 255)."""
        result = pgm_above_average_count(_PGM / "3x1-ramp.pgm")
        assert result == 2

    def test_returns_int(self):
        result = pgm_above_average_count(_PGM / "2x2-gradient.pgm")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["1x1-white.pgm", "2x2-gradient.pgm", "3x1-ramp.pgm"]:
            assert pgm_above_average_count(_PGM / f) >= 0

    def test_gradient_has_more_above_average_than_uniform(self):
        r1 = pgm_above_average_count(_PGM / "1x1-white.pgm")
        r2 = pgm_above_average_count(_PGM / "2x2-gradient.pgm")
        assert r2 > r1


class TestPgmTotalPixelSum:
    """Tests for pgm_total_pixel_sum."""

    def test_1x1_white_sum_is_255(self):
        """1x1-white.pgm has one pixel with value 255."""
        result = pgm_total_pixel_sum(_PGM / "1x1-white.pgm")
        assert result == 255

    def test_2x2_gradient_sum_is_510(self):
        """2x2-gradient.pgm: pixels [0,85,170,255] sum=510."""
        result = pgm_total_pixel_sum(_PGM / "2x2-gradient.pgm")
        assert result == 510

    def test_3x1_ramp_sum_is_383(self):
        """3x1-ramp.pgm: pixels [0,128,255] sum=383."""
        result = pgm_total_pixel_sum(_PGM / "3x1-ramp.pgm")
        assert result == 383

    def test_returns_int(self):
        result = pgm_total_pixel_sum(_PGM / "1x1-white.pgm")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["1x1-white.pgm", "2x2-gradient.pgm", "3x1-ramp.pgm"]:
            assert pgm_total_pixel_sum(_PGM / f) >= 0

    def test_gradient_has_highest_sum(self):
        r1 = pgm_total_pixel_sum(_PGM / "1x1-white.pgm")
        r2 = pgm_total_pixel_sum(_PGM / "2x2-gradient.pgm")
        assert r2 > r1
