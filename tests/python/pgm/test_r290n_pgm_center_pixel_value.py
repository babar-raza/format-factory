"""Tests for pgm_center_pixel_value — closing GAP-PGM-FOSS-PGM_CENTER_P-001."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pgm.pgm_parser import pgm_center_pixel_value

SAMPLES = _REPO / "samples" / "by-format" / "pgm" / "valid"


def test_center_pixel_value_returns_int():
    result = pgm_center_pixel_value(SAMPLES / "2x2-gradient.pgm")
    assert isinstance(result, int)
    assert result >= 0


def test_center_pixel_value_1x1():
    result = pgm_center_pixel_value(SAMPLES / "1x1-white.pgm")
    assert isinstance(result, int)


def test_center_pixel_value_3x1():
    result = pgm_center_pixel_value(SAMPLES / "3x1-ramp.pgm")
    assert isinstance(result, int)
    assert result >= 0
