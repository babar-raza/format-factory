"""Sprint 240 XCF deepening — 2 new analytics functions, 12 tests.

Functions:
  xcf_file_size_mod_7_plus_image_type_times_900_plus_width_times_height_times_num_layers_times_200
  xcf_file_size_mod_6_times_200_plus_image_type_times_300_plus_width_plus_height_times_50

Samples (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf    sz=177, type=0, w=1, h=1, layers=1
  1x1-rgba-blue.xcf  sz=178, type=0, w=1, h=1, layers=1
  2x2-gray.xcf       sz=178, type=1, w=2, h=2, layers=1

Expected:
  xcf_file_size_mod_7_plus_image_type_times_900_plus_width_times_height_times_num_layers_times_200:
    red  = 177%7 + 0*900 + 1*1*1*200 = 2+0+200 = 202
    blue = 178%7 + 0*900 + 1*1*1*200 = 3+0+200 = 203
    gray = 178%7 + 1*900 + 2*2*1*200 = 3+900+800 = 1703

  xcf_file_size_mod_6_times_200_plus_image_type_times_300_plus_width_plus_height_times_50:
    red  = 177%6*200 + 0*300 + (1+1)*50 = 3*200+0+100 = 700
    blue = 178%6*200 + 0*300 + (1+1)*50 = 4*200+0+100 = 900
    gray = 178%6*200 + 1*300 + (2+2)*50 = 4*200+300+200 = 1300
"""
from pathlib import Path

import pytest

from src.python.xcf import (
    xcf_file_size_mod_7_plus_image_type_times_900_plus_width_times_height_times_num_layers_times_200,
    xcf_file_size_mod_6_times_200_plus_image_type_times_300_plus_width_plus_height_times_50,
)

_VALID = Path("samples/by-format/xcf/valid")
RED = _VALID / "1x1-red-rgb.xcf"
BLUE = _VALID / "1x1-rgba-blue.xcf"
GRAY = _VALID / "2x2-gray.xcf"


class TestXcfFileSizeMod7PlusImageTypeTimes900PlusWidthTimesHeightTimesNumLayersTimes200:
    def test_red_value(self):
        assert xcf_file_size_mod_7_plus_image_type_times_900_plus_width_times_height_times_num_layers_times_200(RED) == 202

    def test_blue_value(self):
        assert xcf_file_size_mod_7_plus_image_type_times_900_plus_width_times_height_times_num_layers_times_200(BLUE) == 203

    def test_gray_value(self):
        assert xcf_file_size_mod_7_plus_image_type_times_900_plus_width_times_height_times_num_layers_times_200(GRAY) == 1703

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_7_plus_image_type_times_900_plus_width_times_height_times_num_layers_times_200(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_7_plus_image_type_times_900_plus_width_times_height_times_num_layers_times_200(RED),
            xcf_file_size_mod_7_plus_image_type_times_900_plus_width_times_height_times_num_layers_times_200(BLUE),
            xcf_file_size_mod_7_plus_image_type_times_900_plus_width_times_height_times_num_layers_times_200(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_7_plus_image_type_times_900_plus_width_times_height_times_num_layers_times_200(RED) > 0


class TestXcfFileSizeMod6Times200PlusImageTypeTimes300PlusWidthPlusHeightTimes50:
    def test_red_value(self):
        assert xcf_file_size_mod_6_times_200_plus_image_type_times_300_plus_width_plus_height_times_50(RED) == 700

    def test_blue_value(self):
        assert xcf_file_size_mod_6_times_200_plus_image_type_times_300_plus_width_plus_height_times_50(BLUE) == 900

    def test_gray_value(self):
        assert xcf_file_size_mod_6_times_200_plus_image_type_times_300_plus_width_plus_height_times_50(GRAY) == 1300

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_6_times_200_plus_image_type_times_300_plus_width_plus_height_times_50(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_6_times_200_plus_image_type_times_300_plus_width_plus_height_times_50(RED),
            xcf_file_size_mod_6_times_200_plus_image_type_times_300_plus_width_plus_height_times_50(BLUE),
            xcf_file_size_mod_6_times_200_plus_image_type_times_300_plus_width_plus_height_times_50(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_6_times_200_plus_image_type_times_300_plus_width_plus_height_times_50(RED) > 0
