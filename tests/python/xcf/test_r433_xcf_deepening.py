"""Sprint 204 XCF deepening — 2 new analytics functions, 12 tests.

Functions:
  xcf_file_size_div_width_plus_height_plus_image_type
  xcf_file_size_plus_num_layers_times_image_type_times_100

Samples (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf   sz=177, type=0, w=1, h=1, layers=1
  1x1-rgba-blue.xcf sz=178, type=0, w=1, h=1, layers=1
  2x2-gray.xcf      sz=178, type=1, w=2, h=2, layers=1

Expected:
  xcf_file_size_div_width_plus_height_plus_image_type:
    red  = 177 // (1+1+0) = 88
    blue = 178 // (1+1+0) = 89
    gray = 178 // (2+2+1) = 35

  xcf_file_size_plus_num_layers_times_image_type_times_100:
    red  = 177 + 1*0*100 = 177
    blue = 178 + 1*0*100 = 178
    gray = 178 + 1*1*100 = 278
"""
from pathlib import Path

import pytest

from src.python.xcf import (
    xcf_file_size_div_width_plus_height_plus_image_type,
    xcf_file_size_plus_num_layers_times_image_type_times_100,
)

_VALID = Path("samples/by-format/xcf/valid")
RED = _VALID / "1x1-red-rgb.xcf"
BLUE = _VALID / "1x1-rgba-blue.xcf"
GRAY = _VALID / "2x2-gray.xcf"


class TestXcfFileSizeDivWidthPlusHeightPlusImageType:
    def test_red_value(self):
        assert xcf_file_size_div_width_plus_height_plus_image_type(RED) == 88

    def test_blue_value(self):
        assert xcf_file_size_div_width_plus_height_plus_image_type(BLUE) == 89

    def test_gray_value(self):
        assert xcf_file_size_div_width_plus_height_plus_image_type(GRAY) == 35

    def test_returns_int(self):
        assert isinstance(xcf_file_size_div_width_plus_height_plus_image_type(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_div_width_plus_height_plus_image_type(RED),
            xcf_file_size_div_width_plus_height_plus_image_type(BLUE),
            xcf_file_size_div_width_plus_height_plus_image_type(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_div_width_plus_height_plus_image_type(RED) > 0


class TestXcfFileSizePlusNumLayersTimesImageTypeTimes100:
    def test_red_value(self):
        assert xcf_file_size_plus_num_layers_times_image_type_times_100(RED) == 177

    def test_blue_value(self):
        assert xcf_file_size_plus_num_layers_times_image_type_times_100(BLUE) == 178

    def test_gray_value(self):
        assert xcf_file_size_plus_num_layers_times_image_type_times_100(GRAY) == 278

    def test_returns_int(self):
        assert isinstance(xcf_file_size_plus_num_layers_times_image_type_times_100(RED), int)

    def test_gray_largest(self):
        assert xcf_file_size_plus_num_layers_times_image_type_times_100(GRAY) > xcf_file_size_plus_num_layers_times_image_type_times_100(BLUE)

    def test_positive(self):
        assert xcf_file_size_plus_num_layers_times_image_type_times_100(RED) > 0
