"""Sprint 198 XCF deepening — 2 new analytics functions, 12 tests.

Functions:
  xcf_file_size_plus_image_type_plus_width_plus_height
  xcf_file_size_times_layers_times_image_type_plus_1_div_2

Samples (all in samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf   sz=177, type=0, w=1, h=1, layers=1
  1x1-rgba-blue.xcf sz=178, type=0, w=1, h=1, layers=1
  2x2-gray.xcf      sz=178, type=1, w=2, h=2, layers=1

Expected:
  xcf_file_size_plus_image_type_plus_width_plus_height:
    red  = 177+0+1+1 = 179
    blue = 178+0+1+1 = 180
    gray = 178+1+2+2 = 183

  xcf_file_size_times_layers_times_image_type_plus_1_div_2:
    red  = 177*1*(0+1)//2 = 88
    blue = 178*1*(0+1)//2 = 89
    gray = 178*1*(1+1)//2 = 178
"""
from pathlib import Path

import pytest

from src.python.xcf import (
    xcf_file_size_plus_image_type_plus_width_plus_height,
    xcf_file_size_times_layers_times_image_type_plus_1_div_2,
)

_VALID = Path("samples/by-format/xcf/valid")
RED = _VALID / "1x1-red-rgb.xcf"
BLUE = _VALID / "1x1-rgba-blue.xcf"
GRAY = _VALID / "2x2-gray.xcf"


class TestXcfFileSizePlusImageTypePlusWidthPlusHeight:
    def test_red_value(self):
        assert xcf_file_size_plus_image_type_plus_width_plus_height(RED) == 179

    def test_blue_value(self):
        assert xcf_file_size_plus_image_type_plus_width_plus_height(BLUE) == 180

    def test_gray_value(self):
        assert xcf_file_size_plus_image_type_plus_width_plus_height(GRAY) == 183

    def test_returns_int(self):
        assert isinstance(xcf_file_size_plus_image_type_plus_width_plus_height(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_plus_image_type_plus_width_plus_height(RED),
            xcf_file_size_plus_image_type_plus_width_plus_height(BLUE),
            xcf_file_size_plus_image_type_plus_width_plus_height(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_plus_image_type_plus_width_plus_height(RED) > 0


class TestXcfFileSizeTimesLayersTimesImageTypePlus1Div2:
    def test_red_value(self):
        assert xcf_file_size_times_layers_times_image_type_plus_1_div_2(RED) == 88

    def test_blue_value(self):
        assert xcf_file_size_times_layers_times_image_type_plus_1_div_2(BLUE) == 89

    def test_gray_value(self):
        assert xcf_file_size_times_layers_times_image_type_plus_1_div_2(GRAY) == 178

    def test_returns_int(self):
        assert isinstance(xcf_file_size_times_layers_times_image_type_plus_1_div_2(RED), int)

    def test_gray_double_red(self):
        # gray type=1 so doubled vs red type=0 (same size 178 vs 177, close)
        assert xcf_file_size_times_layers_times_image_type_plus_1_div_2(GRAY) > xcf_file_size_times_layers_times_image_type_plus_1_div_2(RED)

    def test_positive(self):
        assert xcf_file_size_times_layers_times_image_type_plus_1_div_2(RED) > 0
