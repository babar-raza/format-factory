"""Tests for QOI image analytics extension functions (batch 2) in qoi_image_analytics.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.qoi.qoi_image_analytics import (
    qoi_channels,
    qoi_is_single_pixel,
    qoi_aspect_ratio,
    qoi_is_opaque,
    qoi_unique_pixel_count,
    qoi_is_srgb,
)

SAMPLES = Path("samples/by-format/qoi/valid")
RED_1X1   = SAMPLES / "1x1-red.qoi"       # w=1 h=1 channels=4 colorspace=0, pixel=(255,0,0,255)
BLACK_2X2 = SAMPLES / "2x2-black.qoi"     # w=2 h=2 channels=4 colorspace=0, all (0,0,0,255)
GRAD_4X1  = SAMPLES / "4x1-gradient.qoi"  # w=4 h=1 channels=3 colorspace=0


# qoi_channels
def test_channels_rgba():
    assert qoi_channels(RED_1X1) == 4

def test_channels_rgb():
    assert qoi_channels(GRAD_4X1) == 3

def test_channels_black_2x2():
    assert qoi_channels(BLACK_2X2) == 4

def test_channels_returns_int():
    assert isinstance(qoi_channels(RED_1X1), int)


# qoi_is_single_pixel
def test_is_single_pixel_1x1():
    assert qoi_is_single_pixel(RED_1X1) is True

def test_is_single_pixel_2x2():
    assert qoi_is_single_pixel(BLACK_2X2) is False

def test_is_single_pixel_4x1():
    assert qoi_is_single_pixel(GRAD_4X1) is False

def test_is_single_pixel_returns_bool():
    assert isinstance(qoi_is_single_pixel(RED_1X1), bool)


# qoi_aspect_ratio
def test_aspect_ratio_1x1():
    assert qoi_aspect_ratio(RED_1X1) == pytest.approx(1.0)

def test_aspect_ratio_4x1():
    assert qoi_aspect_ratio(GRAD_4X1) == pytest.approx(4.0)

def test_aspect_ratio_2x2():
    assert qoi_aspect_ratio(BLACK_2X2) == pytest.approx(1.0)

def test_aspect_ratio_returns_float():
    assert isinstance(qoi_aspect_ratio(RED_1X1), float)


# qoi_is_opaque
def test_is_opaque_red_1x1():
    assert qoi_is_opaque(RED_1X1) is True

def test_is_opaque_black_2x2():
    assert qoi_is_opaque(BLACK_2X2) is True

def test_is_opaque_rgb_image():
    assert qoi_is_opaque(GRAD_4X1) is True

def test_is_opaque_returns_bool():
    assert isinstance(qoi_is_opaque(RED_1X1), bool)


# qoi_unique_pixel_count
def test_unique_pixel_count_1x1():
    assert qoi_unique_pixel_count(RED_1X1) == 1

def test_unique_pixel_count_2x2_black():
    assert qoi_unique_pixel_count(BLACK_2X2) == 1

def test_unique_pixel_count_returns_int():
    assert isinstance(qoi_unique_pixel_count(RED_1X1), int)


# qoi_is_srgb
def test_is_srgb_1x1():
    assert qoi_is_srgb(RED_1X1) is True

def test_is_srgb_2x2():
    assert qoi_is_srgb(BLACK_2X2) is True

def test_is_srgb_returns_bool():
    assert isinstance(qoi_is_srgb(RED_1X1), bool)
