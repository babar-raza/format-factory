"""Sprint 207 XCF deepening — 2 new analytics functions, 12 tests.

Functions:
  xcf_file_size_mod_100_plus_image_type_times_10_plus_width
  xcf_width_times_height_times_image_type_plus_1_plus_file_size_mod_10

Samples (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf   sz=177, type=0, w=1, h=1, layers=1
  1x1-rgba-blue.xcf sz=178, type=0, w=1, h=1, layers=1
  2x2-gray.xcf      sz=178, type=1, w=2, h=2, layers=1

Expected:
  xcf_file_size_mod_100_plus_image_type_times_10_plus_width:
    red  = 177%100 + 0*10 + 1 = 78
    blue = 178%100 + 0*10 + 1 = 79
    gray = 178%100 + 1*10 + 2 = 90

  xcf_width_times_height_times_image_type_plus_1_plus_file_size_mod_10:
    red  = 1*1*(0+1) + 177%10 = 8
    blue = 1*1*(0+1) + 178%10 = 9
    gray = 2*2*(1+1) + 178%10 = 16
"""
from pathlib import Path

import pytest

from src.python.xcf import (
    xcf_file_size_mod_100_plus_image_type_times_10_plus_width,
    xcf_width_times_height_times_image_type_plus_1_plus_file_size_mod_10,
)

_VALID = Path("samples/by-format/xcf/valid")
RED = _VALID / "1x1-red-rgb.xcf"
BLUE = _VALID / "1x1-rgba-blue.xcf"
GRAY = _VALID / "2x2-gray.xcf"


class TestXcfFileSizeMod100PlusImageTypeTimes10PlusWidth:
    def test_red_value(self):
        assert xcf_file_size_mod_100_plus_image_type_times_10_plus_width(RED) == 78

    def test_blue_value(self):
        assert xcf_file_size_mod_100_plus_image_type_times_10_plus_width(BLUE) == 79

    def test_gray_value(self):
        assert xcf_file_size_mod_100_plus_image_type_times_10_plus_width(GRAY) == 90

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_100_plus_image_type_times_10_plus_width(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_100_plus_image_type_times_10_plus_width(RED),
            xcf_file_size_mod_100_plus_image_type_times_10_plus_width(BLUE),
            xcf_file_size_mod_100_plus_image_type_times_10_plus_width(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_100_plus_image_type_times_10_plus_width(RED) > 0


class TestXcfWidthTimesHeightTimesImageTypePlus1PlusFileSizeMod10:
    def test_red_value(self):
        assert xcf_width_times_height_times_image_type_plus_1_plus_file_size_mod_10(RED) == 8

    def test_blue_value(self):
        assert xcf_width_times_height_times_image_type_plus_1_plus_file_size_mod_10(BLUE) == 9

    def test_gray_value(self):
        assert xcf_width_times_height_times_image_type_plus_1_plus_file_size_mod_10(GRAY) == 16

    def test_returns_int(self):
        assert isinstance(xcf_width_times_height_times_image_type_plus_1_plus_file_size_mod_10(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_width_times_height_times_image_type_plus_1_plus_file_size_mod_10(RED),
            xcf_width_times_height_times_image_type_plus_1_plus_file_size_mod_10(BLUE),
            xcf_width_times_height_times_image_type_plus_1_plus_file_size_mod_10(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_width_times_height_times_image_type_plus_1_plus_file_size_mod_10(RED) > 0
