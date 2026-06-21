"""Tests for pgm_below_midpoint_count and pgm_nonzero_pixel_count (Sprint 72)."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from pgm.pgm_parser import pgm_below_midpoint_count, pgm_nonzero_pixel_count

PGM = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "pgm" / "valid"


class TestPgmBelowMidpointCount:
    def test_all_white(self):
        assert pgm_below_midpoint_count(PGM / "1x1-white.pgm") == 0

    def test_gradient(self):
        assert pgm_below_midpoint_count(PGM / "2x2-gradient.pgm") == 2

    def test_ramp(self):
        assert pgm_below_midpoint_count(PGM / "3x1-ramp.pgm") == 1

    def test_returns_int(self):
        assert isinstance(pgm_below_midpoint_count(PGM / "1x1-white.pgm"), int)

    def test_nonnegative(self):
        for f in ["1x1-white.pgm", "2x2-gradient.pgm", "3x1-ramp.pgm"]:
            assert pgm_below_midpoint_count(PGM / f) >= 0


class TestPgmNonzeroPixelCount:
    def test_white_single(self):
        assert pgm_nonzero_pixel_count(PGM / "1x1-white.pgm") == 1

    def test_gradient_three(self):
        assert pgm_nonzero_pixel_count(PGM / "2x2-gradient.pgm") == 3

    def test_ramp_two(self):
        assert pgm_nonzero_pixel_count(PGM / "3x1-ramp.pgm") == 2

    def test_returns_int(self):
        assert isinstance(pgm_nonzero_pixel_count(PGM / "1x1-white.pgm"), int)

    def test_nonnegative(self):
        for f in ["1x1-white.pgm", "2x2-gradient.pgm", "3x1-ramp.pgm"]:
            assert pgm_nonzero_pixel_count(PGM / f) >= 0
