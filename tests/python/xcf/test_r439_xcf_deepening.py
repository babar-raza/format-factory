"""Sprint 210 XCF deepening — 2 new analytics functions, 12 tests.

Functions:
  xcf_file_size_plus_image_type_plus_num_layers_times_10
  xcf_file_size_times_3_div_7_plus_image_type_times_width

Samples (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf   sz=177, type=0, w=1, h=1, layers=1
  1x1-rgba-blue.xcf sz=178, type=0, w=1, h=1, layers=1
  2x2-gray.xcf      sz=178, type=1, w=2, h=2, layers=1

Expected:
  xcf_file_size_plus_image_type_plus_num_layers_times_10:
    red  = 177 + 0 + 1*10 = 187
    blue = 178 + 0 + 1*10 = 188
    gray = 178 + 1 + 1*10 = 189

  xcf_file_size_times_3_div_7_plus_image_type_times_width:
    red  = 177*3//7 + 0*1 = 75
    blue = 178*3//7 + 0*1 = 76
    gray = 178*3//7 + 1*2 = 78
"""
from pathlib import Path

import pytest

from src.python.xcf import (
    xcf_file_size_plus_image_type_plus_num_layers_times_10,
    xcf_file_size_times_3_div_7_plus_image_type_times_width,
)

_VALID = Path("samples/by-format/xcf/valid")
RED = _VALID / "1x1-red-rgb.xcf"
BLUE = _VALID / "1x1-rgba-blue.xcf"
GRAY = _VALID / "2x2-gray.xcf"


class TestXcfFileSizePlusImageTypePlusNumLayersTimes10:
    def test_red_value(self):
        assert xcf_file_size_plus_image_type_plus_num_layers_times_10(RED) == 187

    def test_blue_value(self):
        assert xcf_file_size_plus_image_type_plus_num_layers_times_10(BLUE) == 188

    def test_gray_value(self):
        assert xcf_file_size_plus_image_type_plus_num_layers_times_10(GRAY) == 189

    def test_returns_int(self):
        assert isinstance(xcf_file_size_plus_image_type_plus_num_layers_times_10(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_plus_image_type_plus_num_layers_times_10(RED),
            xcf_file_size_plus_image_type_plus_num_layers_times_10(BLUE),
            xcf_file_size_plus_image_type_plus_num_layers_times_10(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_plus_image_type_plus_num_layers_times_10(RED) > 0


class TestXcfFileSizeTimes3Div7PlusImageTypeTimesWidth:
    def test_red_value(self):
        assert xcf_file_size_times_3_div_7_plus_image_type_times_width(RED) == 75

    def test_blue_value(self):
        assert xcf_file_size_times_3_div_7_plus_image_type_times_width(BLUE) == 76

    def test_gray_value(self):
        assert xcf_file_size_times_3_div_7_plus_image_type_times_width(GRAY) == 78

    def test_returns_int(self):
        assert isinstance(xcf_file_size_times_3_div_7_plus_image_type_times_width(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_times_3_div_7_plus_image_type_times_width(RED),
            xcf_file_size_times_3_div_7_plus_image_type_times_width(BLUE),
            xcf_file_size_times_3_div_7_plus_image_type_times_width(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_times_3_div_7_plus_image_type_times_width(RED) > 0
