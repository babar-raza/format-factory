"""Tests for XCF Sprint 50 gap closure.

Closes:
  GAP-XCF-FOSS-XCF_LAYER_NA-001  (Xcf Layer Name List)
  GAP-XCF-FOSS-XCF_COLOR_DE-001  (Xcf Color Depth)
  GAP-XCF-FOSS-XCF_WIDTH_PL-001  (Xcf Width Plus Height)
  GAP-XCF-FOSS-XCF_LAYER_PI-001  (Xcf Layer Pixel Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_layer_name_list,
    xcf_color_depth,
    xcf_width_plus_height,
    xcf_layer_pixel_count,
)

_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"
_RED_1X1 = str(_DIR / "1x1-red-rgb.xcf")
_BLUE_1X1 = str(_DIR / "1x1-rgba-blue.xcf")
_GRAY_2X2 = str(_DIR / "2x2-gray.xcf")


class TestXcfLayerNameList:
    def test_return_type(self):
        assert isinstance(xcf_layer_name_list(_RED_1X1), list)

    def test_exact_layer0_for_red(self):
        assert xcf_layer_name_list(_RED_1X1) == ["Layer 0"]

    def test_exact_layer0_for_blue(self):
        assert xcf_layer_name_list(_BLUE_1X1) == ["Layer 0"]

    def test_exact_layer0_for_gray(self):
        assert xcf_layer_name_list(_GRAY_2X2) == ["Layer 0"]

    def test_length_one(self):
        assert len(xcf_layer_name_list(_RED_1X1)) == 1

    def test_consistent_across_calls(self):
        assert xcf_layer_name_list(_RED_1X1) == xcf_layer_name_list(_RED_1X1)


class TestXcfColorDepth:
    def test_return_type(self):
        assert isinstance(xcf_color_depth(_RED_1X1), int)

    def test_exact_24_for_rgb(self):
        assert xcf_color_depth(_RED_1X1) == 24

    def test_exact_8_for_gray(self):
        assert xcf_color_depth(_GRAY_2X2) == 8

    def test_positive(self):
        assert xcf_color_depth(_RED_1X1) > 0

    def test_consistent_across_calls(self):
        assert xcf_color_depth(_RED_1X1) == xcf_color_depth(_RED_1X1)


class TestXcfWidthPlusHeight:
    def test_return_type(self):
        assert isinstance(xcf_width_plus_height(_RED_1X1), int)

    def test_exact_2_for_1x1(self):
        assert xcf_width_plus_height(_RED_1X1) == 2

    def test_exact_2_for_1x1_blue(self):
        assert xcf_width_plus_height(_BLUE_1X1) == 2

    def test_exact_4_for_2x2(self):
        assert xcf_width_plus_height(_GRAY_2X2) == 4

    def test_positive(self):
        assert xcf_width_plus_height(_RED_1X1) > 0

    def test_consistent_across_calls(self):
        assert xcf_width_plus_height(_RED_1X1) == xcf_width_plus_height(_RED_1X1)


class TestXcfLayerPixelCount:
    def test_return_type(self):
        assert isinstance(xcf_layer_pixel_count(_RED_1X1), int)

    def test_exact_1_for_1x1_red(self):
        assert xcf_layer_pixel_count(_RED_1X1) == 1

    def test_exact_1_for_1x1_blue(self):
        assert xcf_layer_pixel_count(_BLUE_1X1) == 1

    def test_exact_4_for_2x2(self):
        assert xcf_layer_pixel_count(_GRAY_2X2) == 4

    def test_positive(self):
        assert xcf_layer_pixel_count(_RED_1X1) > 0

    def test_consistent_across_calls(self):
        assert xcf_layer_pixel_count(_RED_1X1) == xcf_layer_pixel_count(_RED_1X1)
