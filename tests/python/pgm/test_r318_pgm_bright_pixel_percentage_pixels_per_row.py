"""Tests for pgm_bright_pixel_percentage and pgm_pixels_per_row (Sprint 108, R318)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_parser import pgm_bright_pixel_percentage, pgm_pixels_per_row

PGM = _REPO / "samples" / "by-format" / "pgm" / "valid"


def test_bright_pct_white():
    assert abs(pgm_bright_pixel_percentage(PGM / "1x1-white.pgm") - 100.0) < 0.1


def test_bright_pct_gradient():
    assert abs(pgm_bright_pixel_percentage(PGM / "2x2-gradient.pgm") - 50.0) < 0.1


def test_bright_pct_ramp():
    assert abs(pgm_bright_pixel_percentage(PGM / "3x1-ramp.pgm") - 66.67) < 0.1


def test_bright_pct_returns_float():
    assert isinstance(pgm_bright_pixel_percentage(PGM / "1x1-white.pgm"), float)


def test_bright_pct_bounded():
    pct = pgm_bright_pixel_percentage(PGM / "2x2-gradient.pgm")
    assert 0.0 <= pct <= 100.0


def test_ppr_1x1():
    assert abs(pgm_pixels_per_row(PGM / "1x1-white.pgm") - 1.0) < 0.01


def test_ppr_2x2():
    assert abs(pgm_pixels_per_row(PGM / "2x2-gradient.pgm") - 2.0) < 0.01


def test_ppr_3x1():
    assert abs(pgm_pixels_per_row(PGM / "3x1-ramp.pgm") - 3.0) < 0.01


def test_ppr_returns_float():
    assert isinstance(pgm_pixels_per_row(PGM / "1x1-white.pgm"), float)


def test_ppr_positive():
    assert pgm_pixels_per_row(PGM / "2x2-gradient.pgm") > 0.0
