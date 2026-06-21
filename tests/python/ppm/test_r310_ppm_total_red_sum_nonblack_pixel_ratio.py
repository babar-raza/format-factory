"""Tests for ppm_total_red_sum and ppm_nonblack_pixel_ratio (Sprint 100, R310)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_total_red_sum, ppm_nonblack_pixel_ratio

PPM = _REPO / "samples" / "by-format" / "ppm" / "valid"


def test_total_red_sum_red():
    assert ppm_total_red_sum(PPM / "1x1-red.ppm") == 255


def test_total_red_sum_rgbw():
    assert ppm_total_red_sum(PPM / "2x2-rgbw.ppm") == 510


def test_total_red_sum_gradient():
    assert ppm_total_red_sum(PPM / "3x1-gradient.ppm") == 383


def test_total_red_sum_returns_int():
    assert isinstance(ppm_total_red_sum(PPM / "1x1-red.ppm"), int)


def test_total_red_sum_nonnegative():
    assert ppm_total_red_sum(PPM / "3x1-gradient.ppm") >= 0


def test_nonblack_ratio_red():
    assert abs(ppm_nonblack_pixel_ratio(PPM / "1x1-red.ppm") - 1.0) < 0.001


def test_nonblack_ratio_rgbw():
    assert abs(ppm_nonblack_pixel_ratio(PPM / "2x2-rgbw.ppm") - 1.0) < 0.001


def test_nonblack_ratio_gradient():
    assert abs(ppm_nonblack_pixel_ratio(PPM / "3x1-gradient.ppm") - 0.6667) < 0.001


def test_nonblack_ratio_returns_float():
    assert isinstance(ppm_nonblack_pixel_ratio(PPM / "1x1-red.ppm"), float)


def test_nonblack_ratio_nonnegative():
    assert ppm_nonblack_pixel_ratio(PPM / "2x2-rgbw.ppm") >= 0.0
