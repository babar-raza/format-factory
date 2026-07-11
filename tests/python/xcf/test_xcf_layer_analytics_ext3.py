"""Tests for xcf_layer_analytics extension functions (ext3 batch)."""
from __future__ import annotations

from pathlib import Path

from xcf.xcf_layer_analytics import (
    xcf_last_layer_name,
    xcf_is_portrait,
    xcf_is_indexed,
    xcf_total_pixels,
    xcf_version,
    xcf_has_multiple_layers,
)

SAMPLES = Path("samples/by-format/xcf/valid")
RGB_1X1 = SAMPLES / "1x1-red-rgb.xcf"
GRAY_2X2 = SAMPLES / "2x2-gray.xcf"
RGBA_1X1 = SAMPLES / "1x1-rgba-blue.xcf"


# --- xcf_last_layer_name ---

def test_last_layer_name_returns_str():
    assert isinstance(xcf_last_layer_name(RGB_1X1), str)


def test_last_layer_name_nonempty():
    assert len(xcf_last_layer_name(RGB_1X1)) > 0


# --- xcf_is_portrait ---

def test_is_portrait_1x1_false():
    # 1x1 is square, not portrait
    assert xcf_is_portrait(RGB_1X1) is False


def test_is_portrait_returns_bool():
    assert isinstance(xcf_is_portrait(RGB_1X1), bool)


# --- xcf_is_indexed ---

def test_is_indexed_rgb_false():
    assert xcf_is_indexed(RGB_1X1) is False


def test_is_indexed_gray_false():
    assert xcf_is_indexed(GRAY_2X2) is False


def test_is_indexed_returns_bool():
    assert isinstance(xcf_is_indexed(RGB_1X1), bool)


# --- xcf_total_pixels ---

def test_total_pixels_1x1():
    assert xcf_total_pixels(RGB_1X1) == 1


def test_total_pixels_2x2():
    assert xcf_total_pixels(GRAY_2X2) == 4


def test_total_pixels_returns_int():
    assert isinstance(xcf_total_pixels(RGB_1X1), int)


# --- xcf_version ---

def test_version_returns_str():
    assert isinstance(xcf_version(RGB_1X1), str)


def test_version_nonempty():
    assert len(xcf_version(RGB_1X1)) > 0


# --- xcf_has_multiple_layers ---

def test_has_multiple_layers_returns_bool():
    assert isinstance(xcf_has_multiple_layers(RGB_1X1), bool)


def test_has_multiple_layers_single_false():
    assert xcf_has_multiple_layers(RGB_1X1) is False
