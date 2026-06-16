"""Tests for 5 new XCF analytics functions.

Uses real sample files from samples/by-format/xcf/valid/.
Covers: xcf_total_pixels, xcf_aspect_ratio, xcf_is_square,
    xcf_layers_per_pixel, xcf_is_rgb.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_total_pixels,
    xcf_aspect_ratio,
    xcf_is_square,
    xcf_layers_per_pixel,
    xcf_is_rgb,
)

_SAMPLES = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _SAMPLES / "1x1-red-rgb.xcf"
BLUE = _SAMPLES / "1x1-rgba-blue.xcf"
GRAY = _SAMPLES / "2x2-gray.xcf"


class TestXcfTotalPixels:
    def test_returns_int(self):
        result = xcf_total_pixels(RED)
        assert isinstance(result, int)

    def test_positive(self):
        result = xcf_total_pixels(RED)
        assert result > 0

    def test_1x1_is_1(self):
        result = xcf_total_pixels(RED)
        assert result == 1

    def test_2x2_is_4(self):
        result = xcf_total_pixels(GRAY)
        assert result == 4


class TestXcfAspectRatio:
    def test_returns_float(self):
        result = xcf_aspect_ratio(RED)
        assert isinstance(result, float)

    def test_square_is_one(self):
        result = xcf_aspect_ratio(RED)
        assert result == 1.0

    def test_gray_square(self):
        result = xcf_aspect_ratio(GRAY)
        assert result == 1.0


class TestXcfIsSquare:
    def test_returns_bool(self):
        result = xcf_is_square(RED)
        assert isinstance(result, bool)

    def test_1x1_is_square(self):
        assert xcf_is_square(RED) is True

    def test_2x2_is_square(self):
        assert xcf_is_square(GRAY) is True


class TestXcfLayersPerPixel:
    def test_returns_float(self):
        result = xcf_layers_per_pixel(RED)
        assert isinstance(result, float)

    def test_positive(self):
        result = xcf_layers_per_pixel(RED)
        assert result > 0.0

    def test_gray(self):
        result = xcf_layers_per_pixel(GRAY)
        assert result > 0.0


class TestXcfIsRgb:
    def test_returns_bool(self):
        result = xcf_is_rgb(RED)
        assert isinstance(result, bool)

    def test_red_is_rgb(self):
        assert xcf_is_rgb(RED) is True

    def test_blue_is_rgb(self):
        assert xcf_is_rgb(BLUE) is True
