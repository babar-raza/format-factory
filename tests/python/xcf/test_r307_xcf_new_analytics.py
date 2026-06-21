"""
Sprint 43 — 5 new XCF analytics functions.
Tests: xcf_width_to_height_ratio, xcf_canvas_perimeter,
       xcf_layer_density, xcf_is_portrait, xcf_file_size_kb
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from xcf import (
    xcf_width_to_height_ratio,
    xcf_canvas_perimeter,
    xcf_layer_density,
    xcf_is_portrait,
    xcf_file_size_kb,
)

_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RED = str(_SAMPLES / "1x1-red-rgb.xcf")
_BLUE = str(_SAMPLES / "1x1-rgba-blue.xcf")
_GRAY = str(_SAMPLES / "2x2-gray.xcf")


# --- xcf_width_to_height_ratio ---

def test_width_to_height_ratio_red_is_float():
    assert isinstance(xcf_width_to_height_ratio(_RED), float)


def test_width_to_height_ratio_red_positive():
    assert xcf_width_to_height_ratio(_RED) > 0.0


def test_width_to_height_ratio_gray_positive():
    assert xcf_width_to_height_ratio(_GRAY) > 0.0


def test_width_to_height_ratio_square_is_one():
    result = xcf_width_to_height_ratio(_RED)
    assert result == 1.0  # 1x1


# --- xcf_canvas_perimeter ---

def test_canvas_perimeter_red_is_int():
    assert isinstance(xcf_canvas_perimeter(_RED), int)


def test_canvas_perimeter_red_positive():
    assert xcf_canvas_perimeter(_RED) > 0


def test_canvas_perimeter_gray_positive():
    assert xcf_canvas_perimeter(_GRAY) > 0


def test_canvas_perimeter_gray_larger_than_red():
    assert xcf_canvas_perimeter(_GRAY) >= xcf_canvas_perimeter(_RED)


# --- xcf_layer_density ---

def test_layer_density_red_is_float():
    assert isinstance(xcf_layer_density(_RED), float)


def test_layer_density_red_nonnegative():
    assert xcf_layer_density(_RED) >= 0.0


def test_layer_density_blue_nonnegative():
    assert xcf_layer_density(_BLUE) >= 0.0


def test_layer_density_gray_nonnegative():
    assert xcf_layer_density(_GRAY) >= 0.0


# --- xcf_is_portrait ---

def test_is_portrait_red_is_bool():
    assert isinstance(xcf_is_portrait(_RED), bool)


def test_is_portrait_square_is_false():
    assert not xcf_is_portrait(_RED)  # 1x1 is not portrait


def test_is_portrait_gray_is_bool():
    assert isinstance(xcf_is_portrait(_GRAY), bool)


def test_is_portrait_blue_is_bool():
    assert isinstance(xcf_is_portrait(_BLUE), bool)


# --- xcf_file_size_kb ---

def test_file_size_kb_red_is_float():
    assert isinstance(xcf_file_size_kb(_RED), float)


def test_file_size_kb_red_positive():
    assert xcf_file_size_kb(_RED) > 0.0


def test_file_size_kb_gray_positive():
    assert xcf_file_size_kb(_GRAY) > 0.0


def test_file_size_kb_consistent_with_bytes():
    from pathlib import Path
    size_bytes = Path(_RED).stat().st_size
    assert abs(xcf_file_size_kb(_RED) - size_bytes / 1024.0) < 0.001
