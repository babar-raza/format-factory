"""Tests for PGM analytics deepening (R290K): center_brightness, gradient_magnitude, percentile_value."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import pgm_center_brightness, pgm_gradient_magnitude, pgm_percentile_value

SAMPLES = _REPO / "samples" / "by-format" / "pgm" / "valid"


def test_center_brightness_returns_float():
    result = pgm_center_brightness(SAMPLES / "2x2-gradient.pgm")
    assert isinstance(result, float)
    assert result >= 0.0


def test_center_brightness_1x1():
    result = pgm_center_brightness(SAMPLES / "1x1-white.pgm")
    assert isinstance(result, float)


def test_gradient_magnitude_returns_float():
    result = pgm_gradient_magnitude(SAMPLES / "3x1-ramp.pgm")
    assert isinstance(result, float)
    assert result >= 0.0


def test_gradient_magnitude_uniform():
    result = pgm_gradient_magnitude(SAMPLES / "1x1-white.pgm")
    assert result == 0.0  # single column, no gradient


def test_percentile_value_returns_int():
    result = pgm_percentile_value(SAMPLES / "2x2-gradient.pgm", 50.0)
    assert isinstance(result, int)
    assert result >= 0


def test_percentile_value_extremes():
    low = pgm_percentile_value(SAMPLES / "3x1-ramp.pgm", 0.0)
    high = pgm_percentile_value(SAMPLES / "3x1-ramp.pgm", 100.0)
    assert low <= high
