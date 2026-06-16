"""Tests for xcf_pixel_count_per_layer and xcf_is_multi_pixel (Sprint 60)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from xcf.xcf_parser import xcf_pixel_count_per_layer, xcf_is_multi_pixel

XCF = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "xcf" / "valid"


class TestXcfPixelCountPerLayer:
    def test_1x1_red(self):
        assert xcf_pixel_count_per_layer(XCF / "1x1-red-rgb.xcf") == 1.0

    def test_1x1_rgba(self):
        assert xcf_pixel_count_per_layer(XCF / "1x1-rgba-blue.xcf") == 1.0

    def test_2x2_gray(self):
        assert xcf_pixel_count_per_layer(XCF / "2x2-gray.xcf") == 4.0

    def test_returns_float(self):
        result = xcf_pixel_count_per_layer(XCF / "1x1-red-rgb.xcf")
        assert isinstance(result, float)

    def test_positive(self):
        for f in ["1x1-red-rgb.xcf", "1x1-rgba-blue.xcf", "2x2-gray.xcf"]:
            assert xcf_pixel_count_per_layer(XCF / f) > 0.0


class TestXcfIsMultiPixel:
    def test_1x1_red_not_multi(self):
        assert xcf_is_multi_pixel(XCF / "1x1-red-rgb.xcf") is False

    def test_1x1_rgba_not_multi(self):
        assert xcf_is_multi_pixel(XCF / "1x1-rgba-blue.xcf") is False

    def test_2x2_gray_is_multi(self):
        assert xcf_is_multi_pixel(XCF / "2x2-gray.xcf") is True

    def test_returns_bool(self):
        result = xcf_is_multi_pixel(XCF / "1x1-red-rgb.xcf")
        assert isinstance(result, bool)

    def test_true_for_larger_canvas(self):
        assert xcf_is_multi_pixel(XCF / "2x2-gray.xcf") is True
