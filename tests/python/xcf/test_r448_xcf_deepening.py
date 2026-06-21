"""Sprint 219 XCF deepening — 2 new analytics functions, 12 tests.

Functions:
  xcf_file_size_mod_10_times_100_plus_image_type_times_50_plus_width_times_height
  xcf_file_size_times_2_plus_image_type_times_200_plus_width_times_3

Samples (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf   sz=177, type=0, w=1, h=1, layers=1
  1x1-rgba-blue.xcf sz=178, type=0, w=1, h=1, layers=1
  2x2-gray.xcf      sz=178, type=1, w=2, h=2, layers=1

Expected:
  xcf_file_size_mod_10_times_100_plus_image_type_times_50_plus_width_times_height:
    red  = 177%10*100 + 0*50 + 1*1 = 701
    blue = 178%10*100 + 0*50 + 1*1 = 801
    gray = 178%10*100 + 1*50 + 2*2 = 854

  xcf_file_size_times_2_plus_image_type_times_200_plus_width_times_3:
    red  = 177*2 + 0*200 + 1*3 = 357
    blue = 178*2 + 0*200 + 1*3 = 359
    gray = 178*2 + 1*200 + 2*3 = 562
"""
from pathlib import Path

import pytest

from src.python.xcf import (
    xcf_file_size_mod_10_times_100_plus_image_type_times_50_plus_width_times_height,
    xcf_file_size_times_2_plus_image_type_times_200_plus_width_times_3,
)

_VALID = Path("samples/by-format/xcf/valid")
RED = _VALID / "1x1-red-rgb.xcf"
BLUE = _VALID / "1x1-rgba-blue.xcf"
GRAY = _VALID / "2x2-gray.xcf"


class TestXcfFileSizeMod10Times100PlusImageTypeTimes50PlusWidthTimesHeight:
    def test_red_value(self):
        assert xcf_file_size_mod_10_times_100_plus_image_type_times_50_plus_width_times_height(RED) == 701

    def test_blue_value(self):
        assert xcf_file_size_mod_10_times_100_plus_image_type_times_50_plus_width_times_height(BLUE) == 801

    def test_gray_value(self):
        assert xcf_file_size_mod_10_times_100_plus_image_type_times_50_plus_width_times_height(GRAY) == 854

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_10_times_100_plus_image_type_times_50_plus_width_times_height(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_10_times_100_plus_image_type_times_50_plus_width_times_height(RED),
            xcf_file_size_mod_10_times_100_plus_image_type_times_50_plus_width_times_height(BLUE),
            xcf_file_size_mod_10_times_100_plus_image_type_times_50_plus_width_times_height(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_10_times_100_plus_image_type_times_50_plus_width_times_height(RED) > 0


class TestXcfFileSizeTimes2PlusImageTypeTimes200PlusWidthTimes3:
    def test_red_value(self):
        assert xcf_file_size_times_2_plus_image_type_times_200_plus_width_times_3(RED) == 357

    def test_blue_value(self):
        assert xcf_file_size_times_2_plus_image_type_times_200_plus_width_times_3(BLUE) == 359

    def test_gray_value(self):
        assert xcf_file_size_times_2_plus_image_type_times_200_plus_width_times_3(GRAY) == 562

    def test_returns_int(self):
        assert isinstance(xcf_file_size_times_2_plus_image_type_times_200_plus_width_times_3(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_times_2_plus_image_type_times_200_plus_width_times_3(RED),
            xcf_file_size_times_2_plus_image_type_times_200_plus_width_times_3(BLUE),
            xcf_file_size_times_2_plus_image_type_times_200_plus_width_times_3(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_times_2_plus_image_type_times_200_plus_width_times_3(RED) > 0
