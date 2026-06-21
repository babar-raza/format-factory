"""Sprint 225 XCF deepening — 2 new analytics functions, 12 tests.

Functions:
  xcf_file_size_plus_width_times_100_plus_height_times_10_times_image_type_plus_1
  xcf_file_size_mod_7_times_100_plus_image_type_times_300_plus_num_layers_times_20

Samples (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf   sz=177, type=0, w=1, h=1, layers=1
  1x1-rgba-blue.xcf sz=178, type=0, w=1, h=1, layers=1
  2x2-gray.xcf      sz=178, type=1, w=2, h=2, layers=1

Expected:
  xcf_file_size_plus_width_times_100_plus_height_times_10_times_image_type_plus_1:
    red  = (177 + 1*100 + 1*10) * (0+1) = 287
    blue = (178 + 1*100 + 1*10) * (0+1) = 288
    gray = (178 + 2*100 + 2*10) * (1+1) = 796

  xcf_file_size_mod_7_times_100_plus_image_type_times_300_plus_num_layers_times_20:
    red  = 177%7*100 + 0*300 + 1*20 = 2*100 + 0 + 20 = 220
    blue = 178%7*100 + 0*300 + 1*20 = 3*100 + 0 + 20 = 320
    gray = 178%7*100 + 1*300 + 1*20 = 3*100 + 300 + 20 = 620
"""
from pathlib import Path

import pytest

from src.python.xcf import (
    xcf_file_size_plus_width_times_100_plus_height_times_10_times_image_type_plus_1,
    xcf_file_size_mod_7_times_100_plus_image_type_times_300_plus_num_layers_times_20,
)

_VALID = Path("samples/by-format/xcf/valid")
RED = _VALID / "1x1-red-rgb.xcf"
BLUE = _VALID / "1x1-rgba-blue.xcf"
GRAY = _VALID / "2x2-gray.xcf"


class TestXcfFileSizePlusWidthTimes100PlusHeightTimes10TimesImageTypePlus1:
    def test_red_value(self):
        assert xcf_file_size_plus_width_times_100_plus_height_times_10_times_image_type_plus_1(RED) == 287

    def test_blue_value(self):
        assert xcf_file_size_plus_width_times_100_plus_height_times_10_times_image_type_plus_1(BLUE) == 288

    def test_gray_value(self):
        assert xcf_file_size_plus_width_times_100_plus_height_times_10_times_image_type_plus_1(GRAY) == 796

    def test_returns_int(self):
        assert isinstance(xcf_file_size_plus_width_times_100_plus_height_times_10_times_image_type_plus_1(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_plus_width_times_100_plus_height_times_10_times_image_type_plus_1(RED),
            xcf_file_size_plus_width_times_100_plus_height_times_10_times_image_type_plus_1(BLUE),
            xcf_file_size_plus_width_times_100_plus_height_times_10_times_image_type_plus_1(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_plus_width_times_100_plus_height_times_10_times_image_type_plus_1(RED) > 0


class TestXcfFileSizeMod7Times100PlusImageTypeTimes300PlusNumLayersTimes20:
    def test_red_value(self):
        assert xcf_file_size_mod_7_times_100_plus_image_type_times_300_plus_num_layers_times_20(RED) == 220

    def test_blue_value(self):
        assert xcf_file_size_mod_7_times_100_plus_image_type_times_300_plus_num_layers_times_20(BLUE) == 320

    def test_gray_value(self):
        assert xcf_file_size_mod_7_times_100_plus_image_type_times_300_plus_num_layers_times_20(GRAY) == 620

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_7_times_100_plus_image_type_times_300_plus_num_layers_times_20(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_7_times_100_plus_image_type_times_300_plus_num_layers_times_20(RED),
            xcf_file_size_mod_7_times_100_plus_image_type_times_300_plus_num_layers_times_20(BLUE),
            xcf_file_size_mod_7_times_100_plus_image_type_times_300_plus_num_layers_times_20(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_7_times_100_plus_image_type_times_300_plus_num_layers_times_20(RED) > 0
