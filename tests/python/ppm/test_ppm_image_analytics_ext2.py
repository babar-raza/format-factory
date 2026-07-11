"""Tests for PPM image analytics extension functions (batch 2) in ppm_image_analytics.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_image_analytics import (
    ppm_width,
    ppm_height,
    ppm_maxval,
    ppm_magic,
    ppm_total_pixels,
    ppm_is_standard_depth,
)

SAMPLES = Path("samples/by-format/ppm/valid")
RED_1X1    = SAMPLES / "1x1-red.ppm"       # w=1 h=1 maxval=255 magic=P3, pixel=(255,0,0)
RGBW_2X2   = SAMPLES / "2x2-rgbw.ppm"     # w=2 h=2 maxval=255 magic=P3
GRAD_3X1   = SAMPLES / "3x1-gradient.ppm"  # w=3 h=1 maxval=255 magic=P3


# ppm_width
def test_width_1x1():
    assert ppm_width(RED_1X1) == 1

def test_width_2x2():
    assert ppm_width(RGBW_2X2) == 2

def test_width_3x1():
    assert ppm_width(GRAD_3X1) == 3

def test_width_returns_int():
    assert isinstance(ppm_width(RED_1X1), int)


# ppm_height
def test_height_1x1():
    assert ppm_height(RED_1X1) == 1

def test_height_2x2():
    assert ppm_height(RGBW_2X2) == 2

def test_height_3x1():
    assert ppm_height(GRAD_3X1) == 1

def test_height_returns_int():
    assert isinstance(ppm_height(RED_1X1), int)


# ppm_maxval
def test_maxval_1x1():
    assert ppm_maxval(RED_1X1) == 255

def test_maxval_returns_int():
    assert isinstance(ppm_maxval(RED_1X1), int)


# ppm_magic
def test_magic_1x1():
    assert ppm_magic(RED_1X1) == "P3"

def test_magic_2x2():
    assert ppm_magic(RGBW_2X2) == "P3"

def test_magic_returns_str():
    assert isinstance(ppm_magic(RED_1X1), str)


# ppm_total_pixels
def test_total_pixels_1x1():
    assert ppm_total_pixels(RED_1X1) == 1

def test_total_pixels_2x2():
    assert ppm_total_pixels(RGBW_2X2) == 4

def test_total_pixels_3x1():
    assert ppm_total_pixels(GRAD_3X1) == 3

def test_total_pixels_returns_int():
    assert isinstance(ppm_total_pixels(RED_1X1), int)


# ppm_is_standard_depth
def test_is_standard_depth_1x1():
    assert ppm_is_standard_depth(RED_1X1) is True

def test_is_standard_depth_2x2():
    assert ppm_is_standard_depth(RGBW_2X2) is True

def test_is_standard_depth_returns_bool():
    assert isinstance(ppm_is_standard_depth(RED_1X1), bool)
