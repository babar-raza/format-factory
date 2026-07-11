"""Tests for qoi_image_analytics extension functions (ext3 batch)."""
from __future__ import annotations

from pathlib import Path

from qoi.qoi_image_analytics import (
    qoi_is_linear,
    qoi_has_pixels,
    qoi_pixel_count,
    qoi_avg_red,
    qoi_avg_green,
    qoi_avg_blue,
)

SAMPLES = Path("samples/by-format/qoi/valid")
RED_1X1 = SAMPLES / "1x1-red.qoi"
BLACK_2X2 = SAMPLES / "2x2-black.qoi"
GRAD_4X1 = SAMPLES / "4x1-gradient.qoi"


# --- qoi_is_linear ---

def test_is_linear_returns_bool():
    assert isinstance(qoi_is_linear(RED_1X1), bool)


def test_is_linear_srgb_image_false():
    # 1x1-red is sRGB (colorspace=0), so linear should be False
    assert qoi_is_linear(RED_1X1) is False


# --- qoi_has_pixels ---

def test_has_pixels_red_1x1():
    assert qoi_has_pixels(RED_1X1) is True


def test_has_pixels_returns_bool():
    assert isinstance(qoi_has_pixels(BLACK_2X2), bool)


# --- qoi_pixel_count ---

def test_pixel_count_red_1x1():
    assert qoi_pixel_count(RED_1X1) == 1


def test_pixel_count_2x2():
    assert qoi_pixel_count(BLACK_2X2) == 4


def test_pixel_count_4x1():
    assert qoi_pixel_count(GRAD_4X1) == 4


def test_pixel_count_returns_int():
    assert isinstance(qoi_pixel_count(RED_1X1), int)


# --- qoi_avg_red ---

def test_avg_red_returns_float():
    assert isinstance(qoi_avg_red(RED_1X1), float)


def test_avg_red_range():
    result = qoi_avg_red(RED_1X1)
    assert 0.0 <= result <= 255.0


# --- qoi_avg_green ---

def test_avg_green_returns_float():
    assert isinstance(qoi_avg_green(RED_1X1), float)


def test_avg_green_black_zero():
    # black image has all channels at 0
    result = qoi_avg_green(BLACK_2X2)
    assert result == 0.0


# --- qoi_avg_blue ---

def test_avg_blue_returns_float():
    assert isinstance(qoi_avg_blue(RED_1X1), float)


def test_avg_blue_black_zero():
    result = qoi_avg_blue(BLACK_2X2)
    assert result == 0.0
