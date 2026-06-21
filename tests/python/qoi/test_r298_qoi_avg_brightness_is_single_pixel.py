"""Tests for qoi_avg_brightness and qoi_is_single_pixel (Sprint 88, R298)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_parser import qoi_avg_brightness, qoi_is_single_pixel

QOI = _REPO / "samples" / "by-format" / "qoi" / "valid"


@pytest.fixture
def red1x1():
    return QOI / "1x1-red.qoi"


@pytest.fixture
def black2x2():
    return QOI / "2x2-black.qoi"


@pytest.fixture
def gradient4x1():
    return QOI / "4x1-gradient.qoi"


def test_avg_brightness_red(red1x1):
    assert abs(qoi_avg_brightness(red1x1) - 255.0) < 0.01


def test_avg_brightness_black(black2x2):
    assert abs(qoi_avg_brightness(black2x2) - 0.0) < 0.01


def test_avg_brightness_gradient(gradient4x1):
    assert qoi_avg_brightness(gradient4x1) > 0.0


def test_avg_brightness_returns_float(red1x1):
    assert isinstance(qoi_avg_brightness(red1x1), float)


def test_avg_brightness_nonnegative(black2x2):
    assert qoi_avg_brightness(black2x2) >= 0.0


def test_is_single_pixel_true(red1x1):
    assert qoi_is_single_pixel(red1x1) is True


def test_is_single_pixel_false_2x2(black2x2):
    assert qoi_is_single_pixel(black2x2) is False


def test_is_single_pixel_false_4x1(gradient4x1):
    assert qoi_is_single_pixel(gradient4x1) is False


def test_is_single_pixel_returns_bool(red1x1):
    assert isinstance(qoi_is_single_pixel(red1x1), bool)


def test_is_single_pixel_consistent_with_red(red1x1):
    # 1x1 image must have exactly 1 pixel
    assert qoi_is_single_pixel(red1x1) is True
