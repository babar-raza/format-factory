"""Sprint 237 XCF deepening — 2 new analytics functions, 12 tests.

Functions:
  xcf_file_size_mod_19_plus_image_type_times_800_plus_width_times_height_times_150
  xcf_file_size_mod_4_times_200_plus_image_type_times_250_plus_width_times_100_plus_height_times_80

Samples (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf    sz=177, type=0, w=1, h=1, layers=1
  1x1-rgba-blue.xcf  sz=178, type=0, w=1, h=1, layers=1
  2x2-gray.xcf       sz=178, type=1, w=2, h=2, layers=1

Expected:
  xcf_file_size_mod_19_plus_image_type_times_800_plus_width_times_height_times_150:
    red  = 177%19 + 0*800 + 1*1*150 = 6+0+150 = 156
    blue = 178%19 + 0*800 + 1*1*150 = 7+0+150 = 157
    gray = 178%19 + 1*800 + 2*2*150 = 7+800+600 = 1407

  xcf_file_size_mod_4_times_200_plus_image_type_times_250_plus_width_times_100_plus_height_times_80:
    red  = 177%4*200 + 0*250 + 1*100 + 1*80 = 1*200+0+100+80 = 380
    blue = 178%4*200 + 0*250 + 1*100 + 1*80 = 2*200+0+180 = 580
    gray = 178%4*200 + 1*250 + 2*100 + 2*80 = 2*200+250+200+160 = 1010
"""
from pathlib import Path

import pytest

from src.python.xcf import (
    xcf_file_size_mod_19_plus_image_type_times_800_plus_width_times_height_times_150,
    xcf_file_size_mod_4_times_200_plus_image_type_times_250_plus_width_times_100_plus_height_times_80,
)

_VALID = Path("samples/by-format/xcf/valid")
RED = _VALID / "1x1-red-rgb.xcf"
BLUE = _VALID / "1x1-rgba-blue.xcf"
GRAY = _VALID / "2x2-gray.xcf"


class TestXcfFileSizeMod19PlusImageTypeTimes800PlusWidthTimesHeightTimes150:
    def test_red_value(self):
        assert xcf_file_size_mod_19_plus_image_type_times_800_plus_width_times_height_times_150(RED) == 156

    def test_blue_value(self):
        assert xcf_file_size_mod_19_plus_image_type_times_800_plus_width_times_height_times_150(BLUE) == 157

    def test_gray_value(self):
        assert xcf_file_size_mod_19_plus_image_type_times_800_plus_width_times_height_times_150(GRAY) == 1407

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_19_plus_image_type_times_800_plus_width_times_height_times_150(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_19_plus_image_type_times_800_plus_width_times_height_times_150(RED),
            xcf_file_size_mod_19_plus_image_type_times_800_plus_width_times_height_times_150(BLUE),
            xcf_file_size_mod_19_plus_image_type_times_800_plus_width_times_height_times_150(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_19_plus_image_type_times_800_plus_width_times_height_times_150(RED) > 0


class TestXcfFileSizeMod4Times200PlusImageTypeTimes250PlusWidthTimes100PlusHeightTimes80:
    def test_red_value(self):
        assert xcf_file_size_mod_4_times_200_plus_image_type_times_250_plus_width_times_100_plus_height_times_80(RED) == 380

    def test_blue_value(self):
        assert xcf_file_size_mod_4_times_200_plus_image_type_times_250_plus_width_times_100_plus_height_times_80(BLUE) == 580

    def test_gray_value(self):
        assert xcf_file_size_mod_4_times_200_plus_image_type_times_250_plus_width_times_100_plus_height_times_80(GRAY) == 1010

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_4_times_200_plus_image_type_times_250_plus_width_times_100_plus_height_times_80(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_4_times_200_plus_image_type_times_250_plus_width_times_100_plus_height_times_80(RED),
            xcf_file_size_mod_4_times_200_plus_image_type_times_250_plus_width_times_100_plus_height_times_80(BLUE),
            xcf_file_size_mod_4_times_200_plus_image_type_times_250_plus_width_times_100_plus_height_times_80(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_4_times_200_plus_image_type_times_250_plus_width_times_100_plus_height_times_80(RED) > 0
