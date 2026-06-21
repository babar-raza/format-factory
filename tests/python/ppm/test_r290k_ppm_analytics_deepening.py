"""Tests for PPM analytics deepening (R290K): hue_diversity, center_brightness, max_green_value."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import ppm_hue_diversity, ppm_center_brightness, ppm_max_green_value

SAMPLES = _REPO / "samples" / "by-format" / "ppm" / "valid"


def test_hue_diversity_returns_int():
    result = ppm_hue_diversity(SAMPLES / "2x2-rgbw.ppm")
    assert isinstance(result, int)
    assert result >= 0


def test_hue_diversity_1x1():
    result = ppm_hue_diversity(SAMPLES / "1x1-red.ppm")
    assert isinstance(result, int)


def test_center_brightness_returns_float():
    result = ppm_center_brightness(SAMPLES / "2x2-rgbw.ppm")
    assert isinstance(result, float)
    assert result >= 0.0


def test_center_brightness_1x1():
    result = ppm_center_brightness(SAMPLES / "1x1-red.ppm")
    assert isinstance(result, float)


def test_max_green_value_returns_int():
    result = ppm_max_green_value(SAMPLES / "2x2-rgbw.ppm")
    assert isinstance(result, int)
    assert result >= 0


def test_max_green_value_1x1_red():
    result = ppm_max_green_value(SAMPLES / "1x1-red.ppm")
    assert isinstance(result, int)
    assert result >= 0
