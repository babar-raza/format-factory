"""Tests for XCF layer analytics extension functions (batch 2) in xcf_layer_analytics.py."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_layer_analytics import (
    xcf_width,
    xcf_height,
    xcf_image_type,
    xcf_is_landscape,
    xcf_aspect_ratio,
    xcf_first_layer_name,
)

SAMPLES = Path("samples/by-format/xcf/valid")
RED_1X1  = SAMPLES / "1x1-red-rgb.xcf"    # w=1 h=1 image_type=0 (RGB), layer='Background'
BLUE_1X1 = SAMPLES / "1x1-rgba-blue.xcf"  # w=1 h=1 image_type=0 (RGB), layer='Background'
GRAY_2X2 = SAMPLES / "2x2-gray.xcf"       # w=2 h=2 image_type=1 (Gray), layer='Background'


# xcf_width
def test_width_1x1_red():
    assert xcf_width(RED_1X1) == 1

def test_width_2x2_gray():
    assert xcf_width(GRAY_2X2) == 2

def test_width_returns_int():
    assert isinstance(xcf_width(RED_1X1), int)


# xcf_height
def test_height_1x1_red():
    assert xcf_height(RED_1X1) == 1

def test_height_2x2_gray():
    assert xcf_height(GRAY_2X2) == 2

def test_height_returns_int():
    assert isinstance(xcf_height(RED_1X1), int)


# xcf_image_type
def test_image_type_rgb():
    assert xcf_image_type(RED_1X1) == 0

def test_image_type_gray():
    assert xcf_image_type(GRAY_2X2) == 1

def test_image_type_returns_int():
    assert isinstance(xcf_image_type(RED_1X1), int)


# xcf_is_landscape
def test_is_landscape_1x1_false():
    # square image → not landscape
    assert xcf_is_landscape(RED_1X1) is False

def test_is_landscape_2x2_false():
    assert xcf_is_landscape(GRAY_2X2) is False

def test_is_landscape_returns_bool():
    assert isinstance(xcf_is_landscape(RED_1X1), bool)


# xcf_aspect_ratio
def test_aspect_ratio_1x1():
    assert xcf_aspect_ratio(RED_1X1) == pytest.approx(1.0)

def test_aspect_ratio_2x2():
    assert xcf_aspect_ratio(GRAY_2X2) == pytest.approx(1.0)

def test_aspect_ratio_returns_float():
    assert isinstance(xcf_aspect_ratio(RED_1X1), float)


# xcf_first_layer_name
def test_first_layer_name_red():
    assert xcf_first_layer_name(RED_1X1) == "Background"

def test_first_layer_name_gray():
    assert xcf_first_layer_name(GRAY_2X2) == "Background"

def test_first_layer_name_returns_str():
    assert isinstance(xcf_first_layer_name(RED_1X1), str)
