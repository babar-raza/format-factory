"""Tests for pgm_avg_dark_per_row and pgm_zero_to_nonzero_ratio (Sprint 99, R309)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pgm.pgm_parser import pgm_avg_dark_per_row, pgm_zero_to_nonzero_ratio

PGM = _REPO / "samples" / "by-format" / "pgm" / "valid"


def test_avg_dark_per_row_white():
    assert abs(pgm_avg_dark_per_row(PGM / "1x1-white.pgm") - 0.0) < 0.01


def test_avg_dark_per_row_gradient():
    assert abs(pgm_avg_dark_per_row(PGM / "2x2-gradient.pgm") - 0.5) < 0.01


def test_avg_dark_per_row_ramp():
    assert abs(pgm_avg_dark_per_row(PGM / "3x1-ramp.pgm") - 1.0) < 0.01


def test_avg_dark_per_row_returns_float():
    assert isinstance(pgm_avg_dark_per_row(PGM / "1x1-white.pgm"), float)


def test_avg_dark_per_row_nonnegative():
    assert pgm_avg_dark_per_row(PGM / "1x1-white.pgm") >= 0.0


def test_zero_to_nonzero_ratio_white():
    assert abs(pgm_zero_to_nonzero_ratio(PGM / "1x1-white.pgm") - 0.0) < 0.001


def test_zero_to_nonzero_ratio_gradient():
    assert abs(pgm_zero_to_nonzero_ratio(PGM / "2x2-gradient.pgm") - 0.3333) < 0.001


def test_zero_to_nonzero_ratio_ramp():
    assert abs(pgm_zero_to_nonzero_ratio(PGM / "3x1-ramp.pgm") - 0.5) < 0.001


def test_zero_to_nonzero_ratio_returns_float():
    assert isinstance(pgm_zero_to_nonzero_ratio(PGM / "1x1-white.pgm"), float)


def test_zero_to_nonzero_ratio_nonnegative():
    assert pgm_zero_to_nonzero_ratio(PGM / "2x2-gradient.pgm") >= 0.0
