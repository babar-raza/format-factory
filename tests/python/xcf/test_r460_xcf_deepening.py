"""Sprint 231 XCF deepening — 2 new analytics functions, 12 tests.

Functions:
  xcf_file_size_mod_13_plus_image_type_times_600_plus_width_times_height_times_num_layers_times_100
  xcf_file_size_mod_3_times_100_plus_image_type_times_200_plus_width_times_50_plus_height_times_30

Samples (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf    sz=177, type=0, w=1, h=1, layers=1
  1x1-rgba-blue.xcf  sz=178, type=0, w=1, h=1, layers=1
  2x2-gray.xcf       sz=178, type=1, w=2, h=2, layers=1

Expected:
  xcf_file_size_mod_13_plus_image_type_times_600_plus_width_times_height_times_num_layers_times_100:
    red  = 177%13 + 0*600 + 1*1*1*100 = 8+0+100 = 108
    blue = 178%13 + 0*600 + 1*1*1*100 = 9+0+100 = 109
    gray = 178%13 + 1*600 + 2*2*1*100 = 9+600+400 = 1009

  xcf_file_size_mod_3_times_100_plus_image_type_times_200_plus_width_times_50_plus_height_times_30:
    red  = 177%3*100 + 0*200 + 1*50 + 1*30 = 0+0+50+30 = 80
    blue = 178%3*100 + 0*200 + 1*50 + 1*30 = 100+0+50+30 = 180
    gray = 178%3*100 + 1*200 + 2*50 + 2*30 = 100+200+100+60 = 460
"""
from pathlib import Path

import pytest

from src.python.xcf import (
    xcf_file_size_mod_13_plus_image_type_times_600_plus_width_times_height_times_num_layers_times_100,
    xcf_file_size_mod_3_times_100_plus_image_type_times_200_plus_width_times_50_plus_height_times_30,
)

_VALID = Path("samples/by-format/xcf/valid")
RED = _VALID / "1x1-red-rgb.xcf"
BLUE = _VALID / "1x1-rgba-blue.xcf"
GRAY = _VALID / "2x2-gray.xcf"


class TestXcfFileSizeMod13PlusImageTypeTimes600PlusWidthTimesHeightTimesNumLayersTimes100:
    def test_red_value(self):
        assert xcf_file_size_mod_13_plus_image_type_times_600_plus_width_times_height_times_num_layers_times_100(RED) == 108

    def test_blue_value(self):
        assert xcf_file_size_mod_13_plus_image_type_times_600_plus_width_times_height_times_num_layers_times_100(BLUE) == 109

    def test_gray_value(self):
        assert xcf_file_size_mod_13_plus_image_type_times_600_plus_width_times_height_times_num_layers_times_100(GRAY) == 1009

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_13_plus_image_type_times_600_plus_width_times_height_times_num_layers_times_100(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_13_plus_image_type_times_600_plus_width_times_height_times_num_layers_times_100(RED),
            xcf_file_size_mod_13_plus_image_type_times_600_plus_width_times_height_times_num_layers_times_100(BLUE),
            xcf_file_size_mod_13_plus_image_type_times_600_plus_width_times_height_times_num_layers_times_100(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_13_plus_image_type_times_600_plus_width_times_height_times_num_layers_times_100(RED) > 0


class TestXcfFileSizeMod3Times100PlusImageTypeTimes200PlusWidthTimes50PlusHeightTimes30:
    def test_red_value(self):
        assert xcf_file_size_mod_3_times_100_plus_image_type_times_200_plus_width_times_50_plus_height_times_30(RED) == 80

    def test_blue_value(self):
        assert xcf_file_size_mod_3_times_100_plus_image_type_times_200_plus_width_times_50_plus_height_times_30(BLUE) == 180

    def test_gray_value(self):
        assert xcf_file_size_mod_3_times_100_plus_image_type_times_200_plus_width_times_50_plus_height_times_30(GRAY) == 460

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_3_times_100_plus_image_type_times_200_plus_width_times_50_plus_height_times_30(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_3_times_100_plus_image_type_times_200_plus_width_times_50_plus_height_times_30(RED),
            xcf_file_size_mod_3_times_100_plus_image_type_times_200_plus_width_times_50_plus_height_times_30(BLUE),
            xcf_file_size_mod_3_times_100_plus_image_type_times_200_plus_width_times_50_plus_height_times_30(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_3_times_100_plus_image_type_times_200_plus_width_times_50_plus_height_times_30(RED) > 0
