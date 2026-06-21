"""
Sprint r309: Tests for xcf_is_color and xcf_pixels_exceed_layers.
12 tests total (6 per function).
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_parser import xcf_is_color, xcf_pixels_exceed_layers

_X = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RED = _X / "1x1-red-rgb.xcf"
_BLUE = _X / "1x1-rgba-blue.xcf"
_GRAY = _X / "2x2-gray.xcf"


# --- xcf_is_color ---

def test_is_color_red_returns_bool():
    assert isinstance(xcf_is_color(_RED), bool)

def test_is_color_red_is_true():
    # 1x1-red-rgb: image_type=0 (RGB) → True
    assert xcf_is_color(_RED) is True

def test_is_color_blue_is_true():
    # 1x1-rgba-blue: image_type=0 (RGB) → True
    assert xcf_is_color(_BLUE) is True

def test_is_color_gray_is_false():
    # 2x2-gray: image_type=1 (Grayscale) → False
    assert xcf_is_color(_GRAY) is False

def test_is_color_two_color_one_gray():
    results = [xcf_is_color(p) for p in [_RED, _BLUE, _GRAY]]
    assert results.count(True) == 2
    assert results.count(False) == 1

def test_is_color_both_values_present():
    vals = {xcf_is_color(p) for p in [_RED, _BLUE, _GRAY]}
    assert True in vals and False in vals


# --- xcf_pixels_exceed_layers ---

def test_pixels_exceed_layers_red_returns_bool():
    assert isinstance(xcf_pixels_exceed_layers(_RED), bool)

def test_pixels_exceed_layers_red_is_false():
    # 1x1-red-rgb: 1 pixel, 1 layer → not strictly greater → False
    assert xcf_pixels_exceed_layers(_RED) is False

def test_pixels_exceed_layers_blue_is_false():
    # 1x1-rgba-blue: 1 pixel, 1 layer → False
    assert xcf_pixels_exceed_layers(_BLUE) is False

def test_pixels_exceed_layers_gray_is_true():
    # 2x2-gray: 4 pixels, 1 layer → True
    assert xcf_pixels_exceed_layers(_GRAY) is True

def test_pixels_exceed_layers_only_gray_is_true():
    results = [xcf_pixels_exceed_layers(p) for p in [_RED, _BLUE, _GRAY]]
    assert results.count(True) == 1
    assert results.count(False) == 2

def test_pixels_exceed_layers_consistent_with_is_color():
    # gray is not color AND pixels exceed layers
    assert xcf_is_color(_GRAY) is False
    assert xcf_pixels_exceed_layers(_GRAY) is True
