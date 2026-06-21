"""Sprint 228 XCF deepening — 2 new analytics functions, 12 tests.

Functions:
  xcf_file_size_mod_11_times_200_plus_image_type_times_400_plus_width_times_height_times_50
  xcf_file_size_plus_num_layers_times_200_times_image_type_plus_1_mod_500

Samples (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf    sz=177, type=0, w=1, h=1, layers=1
  1x1-rgba-blue.xcf  sz=178, type=0, w=1, h=1, layers=1
  2x2-gray.xcf       sz=178, type=1, w=2, h=2, layers=1

Expected:
  xcf_file_size_mod_11_times_200_plus_image_type_times_400_plus_width_times_height_times_50:
    red  = 177%11*200 + 0*400 + 1*1*50 = 1*200 + 0 + 50 = 250
    blue = 178%11*200 + 0*400 + 1*1*50 = 2*200 + 0 + 50 = 450
    gray = 178%11*200 + 1*400 + 2*2*50 = 2*200 + 400 + 200 = 1000

  xcf_file_size_plus_num_layers_times_200_times_image_type_plus_1_mod_500:
    red  = (177 + 1*200) * (0+1) % 500 = 377*1%500 = 377
    blue = (178 + 1*200) * (0+1) % 500 = 378*1%500 = 378
    gray = (178 + 1*200) * (1+1) % 500 = 378*2%500 = 756%500 = 256
"""
from pathlib import Path

import pytest

from src.python.xcf import (
    xcf_file_size_mod_11_times_200_plus_image_type_times_400_plus_width_times_height_times_50,
    xcf_file_size_plus_num_layers_times_200_times_image_type_plus_1_mod_500,
)

_VALID = Path("samples/by-format/xcf/valid")
RED = _VALID / "1x1-red-rgb.xcf"
BLUE = _VALID / "1x1-rgba-blue.xcf"
GRAY = _VALID / "2x2-gray.xcf"


class TestXcfFileSizeMod11Times200PlusImageTypeTimes400PlusWidthTimesHeightTimes50:
    def test_red_value(self):
        assert xcf_file_size_mod_11_times_200_plus_image_type_times_400_plus_width_times_height_times_50(RED) == 250

    def test_blue_value(self):
        assert xcf_file_size_mod_11_times_200_plus_image_type_times_400_plus_width_times_height_times_50(BLUE) == 450

    def test_gray_value(self):
        assert xcf_file_size_mod_11_times_200_plus_image_type_times_400_plus_width_times_height_times_50(GRAY) == 1000

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_11_times_200_plus_image_type_times_400_plus_width_times_height_times_50(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_11_times_200_plus_image_type_times_400_plus_width_times_height_times_50(RED),
            xcf_file_size_mod_11_times_200_plus_image_type_times_400_plus_width_times_height_times_50(BLUE),
            xcf_file_size_mod_11_times_200_plus_image_type_times_400_plus_width_times_height_times_50(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_11_times_200_plus_image_type_times_400_plus_width_times_height_times_50(RED) > 0


class TestXcfFileSizePlusNumLayersTimes200TimesImageTypePlus1Mod500:
    def test_red_value(self):
        assert xcf_file_size_plus_num_layers_times_200_times_image_type_plus_1_mod_500(RED) == 377

    def test_blue_value(self):
        assert xcf_file_size_plus_num_layers_times_200_times_image_type_plus_1_mod_500(BLUE) == 378

    def test_gray_value(self):
        assert xcf_file_size_plus_num_layers_times_200_times_image_type_plus_1_mod_500(GRAY) == 256

    def test_returns_int(self):
        assert isinstance(xcf_file_size_plus_num_layers_times_200_times_image_type_plus_1_mod_500(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_plus_num_layers_times_200_times_image_type_plus_1_mod_500(RED),
            xcf_file_size_plus_num_layers_times_200_times_image_type_plus_1_mod_500(BLUE),
            xcf_file_size_plus_num_layers_times_200_times_image_type_plus_1_mod_500(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_plus_num_layers_times_200_times_image_type_plus_1_mod_500(RED) > 0
