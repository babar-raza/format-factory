"""Tests for ppm_avg_luminance and ppm_pixels_per_row (Sprint 109, R319)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_avg_luminance, ppm_pixels_per_row

PPM = _REPO / "samples" / "by-format" / "ppm" / "valid"


def test_avg_lum_red():
    assert abs(ppm_avg_luminance(PPM / "1x1-red.ppm") - 76.245) < 0.01


def test_avg_lum_rgbw():
    assert abs(ppm_avg_luminance(PPM / "2x2-rgbw.ppm") - 127.5) < 0.01


def test_avg_lum_gradient():
    assert abs(ppm_avg_luminance(PPM / "3x1-gradient.ppm") - 127.67) < 0.1


def test_avg_lum_returns_float():
    assert isinstance(ppm_avg_luminance(PPM / "1x1-red.ppm"), float)


def test_avg_lum_nonnegative():
    assert ppm_avg_luminance(PPM / "1x1-red.ppm") >= 0.0


def test_ppr_1x1():
    assert abs(ppm_pixels_per_row(PPM / "1x1-red.ppm") - 1.0) < 0.01


def test_ppr_2x2():
    assert abs(ppm_pixels_per_row(PPM / "2x2-rgbw.ppm") - 2.0) < 0.01


def test_ppr_3x1():
    assert abs(ppm_pixels_per_row(PPM / "3x1-gradient.ppm") - 3.0) < 0.01


def test_ppr_returns_float():
    assert isinstance(ppm_pixels_per_row(PPM / "1x1-red.ppm"), float)


def test_ppr_positive():
    assert ppm_pixels_per_row(PPM / "2x2-rgbw.ppm") > 0.0
