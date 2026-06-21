"""Sprint 246 XCF deepening — 2 new analytics functions, 12 tests.

Functions:
  xcf_file_size_mod_11_plus_image_type_times_1100_plus_width_times_height_plus_num_layers_times_300
  xcf_file_size_mod_10_plus_image_type_times_800_plus_num_layers_times_width_times_height_times_400

Samples (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf    sz=177, type=0, w=1, h=1, layers=1
  1x1-rgba-blue.xcf  sz=178, type=0, w=1, h=1, layers=1
  2x2-gray.xcf       sz=178, type=1, w=2, h=2, layers=1

Expected:
  xcf_file_size_mod_11_plus_image_type_times_1100_plus_width_times_height_plus_num_layers_times_300:
    red  = 177%11 + 0*1100 + (1*1+1)*300 = 1+0+600 = 601
    blue = 178%11 + 0*1100 + (1*1+1)*300 = 2+0+600 = 602
    gray = 178%11 + 1*1100 + (2*2+1)*300 = 2+1100+1500 = 2602

  xcf_file_size_mod_10_plus_image_type_times_800_plus_num_layers_times_width_times_height_times_400:
    red  = 177%10 + 0*800 + 1*1*1*400 = 7+0+400 = 407
    blue = 178%10 + 0*800 + 1*1*1*400 = 8+0+400 = 408
    gray = 178%10 + 1*800 + 1*2*2*400 = 8+800+1600 = 2408
"""
from pathlib import Path

import pytest

from src.python.xcf import (
    xcf_file_size_mod_11_plus_image_type_times_1100_plus_width_times_height_plus_num_layers_times_300,
    xcf_file_size_mod_10_plus_image_type_times_800_plus_num_layers_times_width_times_height_times_400,
)

_VALID = Path("samples/by-format/xcf/valid")
RED = _VALID / "1x1-red-rgb.xcf"
BLUE = _VALID / "1x1-rgba-blue.xcf"
GRAY = _VALID / "2x2-gray.xcf"


class TestXcfFileSizeMod11PlusImageTypeTimes1100PlusWidthTimesHeightPlusNumLayersTimes300:
    def test_red_value(self):
        assert xcf_file_size_mod_11_plus_image_type_times_1100_plus_width_times_height_plus_num_layers_times_300(RED) == 601

    def test_blue_value(self):
        assert xcf_file_size_mod_11_plus_image_type_times_1100_plus_width_times_height_plus_num_layers_times_300(BLUE) == 602

    def test_gray_value(self):
        assert xcf_file_size_mod_11_plus_image_type_times_1100_plus_width_times_height_plus_num_layers_times_300(GRAY) == 2602

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_11_plus_image_type_times_1100_plus_width_times_height_plus_num_layers_times_300(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_11_plus_image_type_times_1100_plus_width_times_height_plus_num_layers_times_300(RED),
            xcf_file_size_mod_11_plus_image_type_times_1100_plus_width_times_height_plus_num_layers_times_300(BLUE),
            xcf_file_size_mod_11_plus_image_type_times_1100_plus_width_times_height_plus_num_layers_times_300(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_11_plus_image_type_times_1100_plus_width_times_height_plus_num_layers_times_300(RED) > 0


class TestXcfFileSizeMod10PlusImageTypeTimes800PlusNumLayersTimesWidthTimesHeightTimes400:
    def test_red_value(self):
        assert xcf_file_size_mod_10_plus_image_type_times_800_plus_num_layers_times_width_times_height_times_400(RED) == 407

    def test_blue_value(self):
        assert xcf_file_size_mod_10_plus_image_type_times_800_plus_num_layers_times_width_times_height_times_400(BLUE) == 408

    def test_gray_value(self):
        assert xcf_file_size_mod_10_plus_image_type_times_800_plus_num_layers_times_width_times_height_times_400(GRAY) == 2408

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_10_plus_image_type_times_800_plus_num_layers_times_width_times_height_times_400(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_10_plus_image_type_times_800_plus_num_layers_times_width_times_height_times_400(RED),
            xcf_file_size_mod_10_plus_image_type_times_800_plus_num_layers_times_width_times_height_times_400(BLUE),
            xcf_file_size_mod_10_plus_image_type_times_800_plus_num_layers_times_width_times_height_times_400(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_10_plus_image_type_times_800_plus_num_layers_times_width_times_height_times_400(RED) > 0
