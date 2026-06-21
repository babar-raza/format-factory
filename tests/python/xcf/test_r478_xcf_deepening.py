"""Sprint 249 XCF deepening — 2 new analytics functions, 12 tests.

Functions:
  xcf_file_size_mod_13_plus_image_type_times_1200_plus_num_layers_plus_1_times_width_times_height_times_500
  xcf_file_size_mod_15_times_30_plus_image_type_times_600_plus_num_layers_times_width_plus_height_times_200

Samples (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf    sz=177, type=0, w=1, h=1, layers=1
  1x1-rgba-blue.xcf  sz=178, type=0, w=1, h=1, layers=1
  2x2-gray.xcf       sz=178, type=1, w=2, h=2, layers=1

Expected:
  xcf_file_size_mod_13_plus_image_type_times_1200_plus_num_layers_plus_1_times_width_times_height_times_500:
    red  = 177%13 + 0*1200 + (1+1)*1*1*500 = 8+0+1000 = 1008
    blue = 178%13 + 0*1200 + (1+1)*1*1*500 = 9+0+1000 = 1009
    gray = 178%13 + 1*1200 + (1+1)*2*2*500 = 9+1200+4000 = 5209

  xcf_file_size_mod_15_times_30_plus_image_type_times_600_plus_num_layers_times_width_plus_height_times_200:
    red  = 177%15*30 + 0*600 + 1*(1+1)*200 = 12*30+0+400 = 760
    blue = 178%15*30 + 0*600 + 1*(1+1)*200 = 13*30+0+400 = 790
    gray = 178%15*30 + 1*600 + 1*(2+2)*200 = 13*30+600+800 = 1790
"""
from pathlib import Path

import pytest

from src.python.xcf import (
    xcf_file_size_mod_13_plus_image_type_times_1200_plus_num_layers_plus_1_times_width_times_height_times_500,
    xcf_file_size_mod_15_times_30_plus_image_type_times_600_plus_num_layers_times_width_plus_height_times_200,
)

_VALID = Path("samples/by-format/xcf/valid")
RED = _VALID / "1x1-red-rgb.xcf"
BLUE = _VALID / "1x1-rgba-blue.xcf"
GRAY = _VALID / "2x2-gray.xcf"


class TestXcfFileSizeMod13PlusImageTypeTimes1200PlusNumLayersPlus1TimesWidthTimesHeightTimes500:
    def test_red_value(self):
        assert xcf_file_size_mod_13_plus_image_type_times_1200_plus_num_layers_plus_1_times_width_times_height_times_500(RED) == 1008

    def test_blue_value(self):
        assert xcf_file_size_mod_13_plus_image_type_times_1200_plus_num_layers_plus_1_times_width_times_height_times_500(BLUE) == 1009

    def test_gray_value(self):
        assert xcf_file_size_mod_13_plus_image_type_times_1200_plus_num_layers_plus_1_times_width_times_height_times_500(GRAY) == 5209

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_13_plus_image_type_times_1200_plus_num_layers_plus_1_times_width_times_height_times_500(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_13_plus_image_type_times_1200_plus_num_layers_plus_1_times_width_times_height_times_500(RED),
            xcf_file_size_mod_13_plus_image_type_times_1200_plus_num_layers_plus_1_times_width_times_height_times_500(BLUE),
            xcf_file_size_mod_13_plus_image_type_times_1200_plus_num_layers_plus_1_times_width_times_height_times_500(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_13_plus_image_type_times_1200_plus_num_layers_plus_1_times_width_times_height_times_500(RED) > 0


class TestXcfFileSizeMod15Times30PlusImageTypeTimes600PlusNumLayersTimesWidthPlusHeightTimes200:
    def test_red_value(self):
        assert xcf_file_size_mod_15_times_30_plus_image_type_times_600_plus_num_layers_times_width_plus_height_times_200(RED) == 760

    def test_blue_value(self):
        assert xcf_file_size_mod_15_times_30_plus_image_type_times_600_plus_num_layers_times_width_plus_height_times_200(BLUE) == 790

    def test_gray_value(self):
        assert xcf_file_size_mod_15_times_30_plus_image_type_times_600_plus_num_layers_times_width_plus_height_times_200(GRAY) == 1790

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_15_times_30_plus_image_type_times_600_plus_num_layers_times_width_plus_height_times_200(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_15_times_30_plus_image_type_times_600_plus_num_layers_times_width_plus_height_times_200(RED),
            xcf_file_size_mod_15_times_30_plus_image_type_times_600_plus_num_layers_times_width_plus_height_times_200(BLUE),
            xcf_file_size_mod_15_times_30_plus_image_type_times_600_plus_num_layers_times_width_plus_height_times_200(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_15_times_30_plus_image_type_times_600_plus_num_layers_times_width_plus_height_times_200(RED) > 0
