"""Sprint 243 XCF deepening — 2 new analytics functions, 12 tests.

Functions:
  xcf_file_size_mod_9_times_100_plus_image_type_times_1000_plus_num_layers_times_500
  xcf_file_size_mod_8_plus_image_type_times_500_plus_width_times_height_plus_1_times_100

Samples (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf    sz=177, type=0, w=1, h=1, layers=1
  1x1-rgba-blue.xcf  sz=178, type=0, w=1, h=1, layers=1
  2x2-gray.xcf       sz=178, type=1, w=2, h=2, layers=1

Expected:
  xcf_file_size_mod_9_times_100_plus_image_type_times_1000_plus_num_layers_times_500:
    red  = 177%9*100 + 0*1000 + 1*500 = 6*100+0+500 = 1100
    blue = 178%9*100 + 0*1000 + 1*500 = 7*100+0+500 = 1200
    gray = 178%9*100 + 1*1000 + 1*500 = 7*100+1000+500 = 2200

  xcf_file_size_mod_8_plus_image_type_times_500_plus_width_times_height_plus_1_times_100:
    red  = 177%8 + 0*500 + (1*1+1)*100 = 1+0+200 = 201
    blue = 178%8 + 0*500 + (1*1+1)*100 = 2+0+200 = 202
    gray = 178%8 + 1*500 + (2*2+1)*100 = 2+500+500 = 1002
"""
from pathlib import Path

import pytest

from src.python.xcf import (
    xcf_file_size_mod_9_times_100_plus_image_type_times_1000_plus_num_layers_times_500,
    xcf_file_size_mod_8_plus_image_type_times_500_plus_width_times_height_plus_1_times_100,
)

_VALID = Path("samples/by-format/xcf/valid")
RED = _VALID / "1x1-red-rgb.xcf"
BLUE = _VALID / "1x1-rgba-blue.xcf"
GRAY = _VALID / "2x2-gray.xcf"


class TestXcfFileSizeMod9Times100PlusImageTypeTimes1000PlusNumLayersTimes500:
    def test_red_value(self):
        assert xcf_file_size_mod_9_times_100_plus_image_type_times_1000_plus_num_layers_times_500(RED) == 1100

    def test_blue_value(self):
        assert xcf_file_size_mod_9_times_100_plus_image_type_times_1000_plus_num_layers_times_500(BLUE) == 1200

    def test_gray_value(self):
        assert xcf_file_size_mod_9_times_100_plus_image_type_times_1000_plus_num_layers_times_500(GRAY) == 2200

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_9_times_100_plus_image_type_times_1000_plus_num_layers_times_500(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_9_times_100_plus_image_type_times_1000_plus_num_layers_times_500(RED),
            xcf_file_size_mod_9_times_100_plus_image_type_times_1000_plus_num_layers_times_500(BLUE),
            xcf_file_size_mod_9_times_100_plus_image_type_times_1000_plus_num_layers_times_500(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_9_times_100_plus_image_type_times_1000_plus_num_layers_times_500(RED) > 0


class TestXcfFileSizeMod8PlusImageTypeTimes500PlusWidthTimesHeightPlus1Times100:
    def test_red_value(self):
        assert xcf_file_size_mod_8_plus_image_type_times_500_plus_width_times_height_plus_1_times_100(RED) == 201

    def test_blue_value(self):
        assert xcf_file_size_mod_8_plus_image_type_times_500_plus_width_times_height_plus_1_times_100(BLUE) == 202

    def test_gray_value(self):
        assert xcf_file_size_mod_8_plus_image_type_times_500_plus_width_times_height_plus_1_times_100(GRAY) == 1002

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_8_plus_image_type_times_500_plus_width_times_height_plus_1_times_100(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_8_plus_image_type_times_500_plus_width_times_height_plus_1_times_100(RED),
            xcf_file_size_mod_8_plus_image_type_times_500_plus_width_times_height_plus_1_times_100(BLUE),
            xcf_file_size_mod_8_plus_image_type_times_500_plus_width_times_height_plus_1_times_100(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_8_plus_image_type_times_500_plus_width_times_height_plus_1_times_100(RED) > 0
