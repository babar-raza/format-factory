"""Sprint 222 XCF deepening — 2 new analytics functions, 12 tests.

Functions:
  xcf_file_size_plus_image_type_times_1000_plus_width_minus_height_times_50
  xcf_file_size_mod_20_plus_image_type_times_500_plus_width_squared_times_10

Samples (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf   sz=177, type=0, w=1, h=1, layers=1
  1x1-rgba-blue.xcf sz=178, type=0, w=1, h=1, layers=1
  2x2-gray.xcf      sz=178, type=1, w=2, h=2, layers=1

Expected:
  xcf_file_size_plus_image_type_times_1000_plus_width_minus_height_times_50:
    red  = 177 + 0*1000 + (1-1)*50 = 177
    blue = 178 + 0*1000 + (1-1)*50 = 178
    gray = 178 + 1*1000 + (2-2)*50 = 1178

  xcf_file_size_mod_20_plus_image_type_times_500_plus_width_squared_times_10:
    red  = 177%20 + 0*500 + 1*1*10 = 17 + 0 + 10 = 27
    blue = 178%20 + 0*500 + 1*1*10 = 18 + 0 + 10 = 28
    gray = 178%20 + 1*500 + 2*2*10 = 18 + 500 + 40 = 558
"""
from pathlib import Path

import pytest

from src.python.xcf import (
    xcf_file_size_plus_image_type_times_1000_plus_width_minus_height_times_50,
    xcf_file_size_mod_20_plus_image_type_times_500_plus_width_squared_times_10,
)

_VALID = Path("samples/by-format/xcf/valid")
RED = _VALID / "1x1-red-rgb.xcf"
BLUE = _VALID / "1x1-rgba-blue.xcf"
GRAY = _VALID / "2x2-gray.xcf"


class TestXcfFileSizePlusImageTypeTimes1000PlusWidthMinusHeightTimes50:
    def test_red_value(self):
        assert xcf_file_size_plus_image_type_times_1000_plus_width_minus_height_times_50(RED) == 177

    def test_blue_value(self):
        assert xcf_file_size_plus_image_type_times_1000_plus_width_minus_height_times_50(BLUE) == 178

    def test_gray_value(self):
        assert xcf_file_size_plus_image_type_times_1000_plus_width_minus_height_times_50(GRAY) == 1178

    def test_returns_int(self):
        assert isinstance(xcf_file_size_plus_image_type_times_1000_plus_width_minus_height_times_50(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_plus_image_type_times_1000_plus_width_minus_height_times_50(RED),
            xcf_file_size_plus_image_type_times_1000_plus_width_minus_height_times_50(BLUE),
            xcf_file_size_plus_image_type_times_1000_plus_width_minus_height_times_50(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_plus_image_type_times_1000_plus_width_minus_height_times_50(RED) > 0


class TestXcfFileSizeMod20PlusImageTypeTimes500PlusWidthSquaredTimes10:
    def test_red_value(self):
        assert xcf_file_size_mod_20_plus_image_type_times_500_plus_width_squared_times_10(RED) == 27

    def test_blue_value(self):
        assert xcf_file_size_mod_20_plus_image_type_times_500_plus_width_squared_times_10(BLUE) == 28

    def test_gray_value(self):
        assert xcf_file_size_mod_20_plus_image_type_times_500_plus_width_squared_times_10(GRAY) == 558

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_20_plus_image_type_times_500_plus_width_squared_times_10(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_20_plus_image_type_times_500_plus_width_squared_times_10(RED),
            xcf_file_size_mod_20_plus_image_type_times_500_plus_width_squared_times_10(BLUE),
            xcf_file_size_mod_20_plus_image_type_times_500_plus_width_squared_times_10(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_20_plus_image_type_times_500_plus_width_squared_times_10(RED) > 0
