"""Tests for XCF layer analytics module."""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf.xcf_layer_analytics import (
    xcf_is_rgb,
    xcf_is_grayscale,
    xcf_is_square,
    xcf_total_pixels,
    xcf_has_single_layer,
    xcf_layer_names,
)

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"       # 1x1, RGB, 1 layer 'Background'
BLUE = SAMPLES / "1x1-rgba-blue.xcf"    # 1x1, RGB, 1 layer 'Background'
GRAY = SAMPLES / "2x2-gray.xcf"          # 2x2, Grayscale, 1 layer 'Background'


# --- xcf_is_rgb ---

def test_is_rgb_red():
    assert xcf_is_rgb(RED) is True


def test_is_rgb_gray():
    assert xcf_is_rgb(GRAY) is False


def test_is_rgb_returns_bool():
    assert isinstance(xcf_is_rgb(RED), bool)


# --- xcf_is_grayscale ---

def test_is_grayscale_gray():
    assert xcf_is_grayscale(GRAY) is True


def test_is_grayscale_red():
    assert xcf_is_grayscale(RED) is False


def test_is_grayscale_returns_bool():
    assert isinstance(xcf_is_grayscale(GRAY), bool)


# --- xcf_is_square ---

def test_is_square_red():
    assert xcf_is_square(RED) is True  # 1x1


def test_is_square_blue():
    assert xcf_is_square(BLUE) is True  # 1x1


def test_is_square_gray():
    assert xcf_is_square(GRAY) is True  # 2x2


def test_is_square_returns_bool():
    assert isinstance(xcf_is_square(RED), bool)


# --- xcf_total_pixels ---

def test_total_pixels_red():
    assert xcf_total_pixels(RED) == 1


def test_total_pixels_gray():
    assert xcf_total_pixels(GRAY) == 4


def test_total_pixels_returns_int():
    assert isinstance(xcf_total_pixels(RED), int)


def test_total_pixels_positive():
    assert xcf_total_pixels(RED) > 0


# --- xcf_has_single_layer ---

def test_has_single_layer_red():
    assert xcf_has_single_layer(RED) is True


def test_has_single_layer_gray():
    assert xcf_has_single_layer(GRAY) is True


def test_has_single_layer_returns_bool():
    assert isinstance(xcf_has_single_layer(RED), bool)


# --- xcf_layer_names ---

def test_layer_names_red():
    assert xcf_layer_names(RED) == ["Background"]


def test_layer_names_gray():
    assert xcf_layer_names(GRAY) == ["Background"]


def test_layer_names_returns_list():
    assert isinstance(xcf_layer_names(RED), list)


def test_layer_names_count_matches_layers():
    names = xcf_layer_names(RED)
    assert len(names) == 1
