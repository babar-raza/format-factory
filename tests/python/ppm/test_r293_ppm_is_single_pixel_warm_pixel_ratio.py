"""Tests for ppm_is_single_pixel and ppm_warm_pixel_ratio (Sprint 83, R293)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import ppm_is_single_pixel, ppm_warm_pixel_ratio

PPM = _REPO / "samples" / "by-format" / "ppm" / "valid"


@pytest.fixture
def red1():
    return PPM / "1x1-red.ppm"


@pytest.fixture
def rgbw():
    return PPM / "2x2-rgbw.ppm"


@pytest.fixture
def gradient():
    return PPM / "3x1-gradient.ppm"


def test_is_single_pixel_red_true(red1):
    assert ppm_is_single_pixel(red1) is True


def test_is_single_pixel_rgbw_false(rgbw):
    assert ppm_is_single_pixel(rgbw) is False


def test_is_single_pixel_gradient_false(gradient):
    assert ppm_is_single_pixel(gradient) is False


def test_is_single_pixel_returns_bool(red1):
    assert isinstance(ppm_is_single_pixel(red1), bool)


def test_warm_pixel_ratio_red_one(red1):
    assert abs(ppm_warm_pixel_ratio(red1) - 1.0) < 0.001


def test_warm_pixel_ratio_rgbw_quarter(rgbw):
    assert abs(ppm_warm_pixel_ratio(rgbw) - 0.25) < 0.001


def test_warm_pixel_ratio_gradient_zero(gradient):
    assert abs(ppm_warm_pixel_ratio(gradient) - 0.0) < 0.001


def test_warm_pixel_ratio_returns_float(red1):
    assert isinstance(ppm_warm_pixel_ratio(red1), float)


def test_warm_pixel_ratio_between_zero_and_one(rgbw):
    r = ppm_warm_pixel_ratio(rgbw)
    assert 0.0 <= r <= 1.0


def test_is_single_pixel_consistent_with_count(red1):
    from ppm.ppm_parser import ppm_pixel_count
    assert ppm_is_single_pixel(red1) == (ppm_pixel_count(red1) == 1)
