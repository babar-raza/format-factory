"""Sprint 216 XCF deepening — 2 new analytics functions, 12 tests.

Functions:
  xcf_file_size_plus_width_times_height_times_image_type_times_100
  xcf_file_size_times_width_plus_height_plus_image_type_times_50

Samples (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf   sz=177, type=0, w=1, h=1, layers=1
  1x1-rgba-blue.xcf sz=178, type=0, w=1, h=1, layers=1
  2x2-gray.xcf      sz=178, type=1, w=2, h=2, layers=1

Expected:
  xcf_file_size_plus_width_times_height_times_image_type_times_100:
    red  = 177 + 1*1*0*100 = 177
    blue = 178 + 1*1*0*100 = 178
    gray = 178 + 2*2*1*100 = 578

  xcf_file_size_times_width_plus_height_plus_image_type_times_50:
    red  = 177*(1+1) + 0*50 = 354
    blue = 178*(1+1) + 0*50 = 356
    gray = 178*(2+2) + 1*50 = 762
"""
from pathlib import Path

import pytest

from src.python.xcf import (
    xcf_file_size_plus_width_times_height_times_image_type_times_100,
    xcf_file_size_times_width_plus_height_plus_image_type_times_50,
)

_VALID = Path("samples/by-format/xcf/valid")
RED = _VALID / "1x1-red-rgb.xcf"
BLUE = _VALID / "1x1-rgba-blue.xcf"
GRAY = _VALID / "2x2-gray.xcf"


class TestXcfFileSizePlusWidthTimesHeightTimesImageTypeTimes100:
    def test_red_value(self):
        assert xcf_file_size_plus_width_times_height_times_image_type_times_100(RED) == 177

    def test_blue_value(self):
        assert xcf_file_size_plus_width_times_height_times_image_type_times_100(BLUE) == 178

    def test_gray_value(self):
        assert xcf_file_size_plus_width_times_height_times_image_type_times_100(GRAY) == 578

    def test_returns_int(self):
        assert isinstance(xcf_file_size_plus_width_times_height_times_image_type_times_100(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_plus_width_times_height_times_image_type_times_100(RED),
            xcf_file_size_plus_width_times_height_times_image_type_times_100(BLUE),
            xcf_file_size_plus_width_times_height_times_image_type_times_100(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_plus_width_times_height_times_image_type_times_100(RED) > 0


class TestXcfFileSizeTimesWidthPlusHeightPlusImageTypeTimes50:
    def test_red_value(self):
        assert xcf_file_size_times_width_plus_height_plus_image_type_times_50(RED) == 354

    def test_blue_value(self):
        assert xcf_file_size_times_width_plus_height_plus_image_type_times_50(BLUE) == 356

    def test_gray_value(self):
        assert xcf_file_size_times_width_plus_height_plus_image_type_times_50(GRAY) == 762

    def test_returns_int(self):
        assert isinstance(xcf_file_size_times_width_plus_height_plus_image_type_times_50(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_times_width_plus_height_plus_image_type_times_50(RED),
            xcf_file_size_times_width_plus_height_plus_image_type_times_50(BLUE),
            xcf_file_size_times_width_plus_height_plus_image_type_times_50(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_times_width_plus_height_plus_image_type_times_50(RED) > 0
