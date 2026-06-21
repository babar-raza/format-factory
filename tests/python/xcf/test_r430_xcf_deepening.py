"""Sprint 201 XCF deepening — 2 new analytics functions, 12 tests.

Functions:
  xcf_file_size_times_width_times_height_div_layers
  xcf_file_size_times_layers_plus_width_plus_height_times_image_type

Samples (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf   sz=177, type=0, w=1, h=1, layers=1
  1x1-rgba-blue.xcf sz=178, type=0, w=1, h=1, layers=1
  2x2-gray.xcf      sz=178, type=1, w=2, h=2, layers=1

Expected:
  xcf_file_size_times_width_times_height_div_layers:
    red  = 177*1*1//1 = 177
    blue = 178*1*1//1 = 178
    gray = 178*2*2//1 = 712

  xcf_file_size_times_layers_plus_width_plus_height_times_image_type:
    red  = 177*1 + (1+1)*0 = 177
    blue = 178*1 + (1+1)*0 = 178
    gray = 178*1 + (2+2)*1 = 182
"""
from pathlib import Path

import pytest

from src.python.xcf import (
    xcf_file_size_times_width_times_height_div_layers,
    xcf_file_size_times_layers_plus_width_plus_height_times_image_type,
)

_VALID = Path("samples/by-format/xcf/valid")
RED = _VALID / "1x1-red-rgb.xcf"
BLUE = _VALID / "1x1-rgba-blue.xcf"
GRAY = _VALID / "2x2-gray.xcf"


class TestXcfFileSizeTimesWidthTimesHeightDivLayers:
    def test_red_value(self):
        assert xcf_file_size_times_width_times_height_div_layers(RED) == 177

    def test_blue_value(self):
        assert xcf_file_size_times_width_times_height_div_layers(BLUE) == 178

    def test_gray_value(self):
        assert xcf_file_size_times_width_times_height_div_layers(GRAY) == 712

    def test_returns_int(self):
        assert isinstance(xcf_file_size_times_width_times_height_div_layers(RED), int)

    def test_gray_largest(self):
        assert xcf_file_size_times_width_times_height_div_layers(GRAY) > xcf_file_size_times_width_times_height_div_layers(BLUE)

    def test_positive(self):
        assert xcf_file_size_times_width_times_height_div_layers(RED) > 0


class TestXcfFileSizeTimesLayersPlusWidthPlusHeightTimesImageType:
    def test_red_value(self):
        assert xcf_file_size_times_layers_plus_width_plus_height_times_image_type(RED) == 177

    def test_blue_value(self):
        assert xcf_file_size_times_layers_plus_width_plus_height_times_image_type(BLUE) == 178

    def test_gray_value(self):
        assert xcf_file_size_times_layers_plus_width_plus_height_times_image_type(GRAY) == 182

    def test_returns_int(self):
        assert isinstance(xcf_file_size_times_layers_plus_width_plus_height_times_image_type(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_times_layers_plus_width_plus_height_times_image_type(RED),
            xcf_file_size_times_layers_plus_width_plus_height_times_image_type(BLUE),
            xcf_file_size_times_layers_plus_width_plus_height_times_image_type(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_times_layers_plus_width_plus_height_times_image_type(RED) > 0
