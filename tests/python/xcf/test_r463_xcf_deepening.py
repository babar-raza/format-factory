"""Sprint 234 XCF deepening — 2 new analytics functions, 12 tests.

Functions:
  xcf_file_size_mod_17_plus_image_type_times_700_plus_width_times_height_times_200
  xcf_file_size_mod_5_times_150_plus_image_type_times_300_plus_num_layers_times_width_times_height

Samples (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf    sz=177, type=0, w=1, h=1, layers=1
  1x1-rgba-blue.xcf  sz=178, type=0, w=1, h=1, layers=1
  2x2-gray.xcf       sz=178, type=1, w=2, h=2, layers=1

Expected:
  xcf_file_size_mod_17_plus_image_type_times_700_plus_width_times_height_times_200:
    red  = 177%17 + 0*700 + 1*1*200 = 7+0+200 = 207
    blue = 178%17 + 0*700 + 1*1*200 = 8+0+200 = 208
    gray = 178%17 + 1*700 + 2*2*200 = 8+700+800 = 1508

  xcf_file_size_mod_5_times_150_plus_image_type_times_300_plus_num_layers_times_width_times_height:
    red  = 177%5*150 + 0*300 + 1*1*1 = 2*150+0+1 = 301
    blue = 178%5*150 + 0*300 + 1*1*1 = 3*150+0+1 = 451
    gray = 178%5*150 + 1*300 + 1*2*2 = 3*150+300+4 = 754
"""
from pathlib import Path

import pytest

from src.python.xcf import (
    xcf_file_size_mod_17_plus_image_type_times_700_plus_width_times_height_times_200,
    xcf_file_size_mod_5_times_150_plus_image_type_times_300_plus_num_layers_times_width_times_height,
)

_VALID = Path("samples/by-format/xcf/valid")
RED = _VALID / "1x1-red-rgb.xcf"
BLUE = _VALID / "1x1-rgba-blue.xcf"
GRAY = _VALID / "2x2-gray.xcf"


class TestXcfFileSizeMod17PlusImageTypeTimes700PlusWidthTimesHeightTimes200:
    def test_red_value(self):
        assert xcf_file_size_mod_17_plus_image_type_times_700_plus_width_times_height_times_200(RED) == 207

    def test_blue_value(self):
        assert xcf_file_size_mod_17_plus_image_type_times_700_plus_width_times_height_times_200(BLUE) == 208

    def test_gray_value(self):
        assert xcf_file_size_mod_17_plus_image_type_times_700_plus_width_times_height_times_200(GRAY) == 1508

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_17_plus_image_type_times_700_plus_width_times_height_times_200(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_17_plus_image_type_times_700_plus_width_times_height_times_200(RED),
            xcf_file_size_mod_17_plus_image_type_times_700_plus_width_times_height_times_200(BLUE),
            xcf_file_size_mod_17_plus_image_type_times_700_plus_width_times_height_times_200(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_17_plus_image_type_times_700_plus_width_times_height_times_200(RED) > 0


class TestXcfFileSizeMod5Times150PlusImageTypeTimes300PlusNumLayersTimesWidthTimesHeight:
    def test_red_value(self):
        assert xcf_file_size_mod_5_times_150_plus_image_type_times_300_plus_num_layers_times_width_times_height(RED) == 301

    def test_blue_value(self):
        assert xcf_file_size_mod_5_times_150_plus_image_type_times_300_plus_num_layers_times_width_times_height(BLUE) == 451

    def test_gray_value(self):
        assert xcf_file_size_mod_5_times_150_plus_image_type_times_300_plus_num_layers_times_width_times_height(GRAY) == 754

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_5_times_150_plus_image_type_times_300_plus_num_layers_times_width_times_height(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_5_times_150_plus_image_type_times_300_plus_num_layers_times_width_times_height(RED),
            xcf_file_size_mod_5_times_150_plus_image_type_times_300_plus_num_layers_times_width_times_height(BLUE),
            xcf_file_size_mod_5_times_150_plus_image_type_times_300_plus_num_layers_times_width_times_height(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_5_times_150_plus_image_type_times_300_plus_num_layers_times_width_times_height(RED) > 0
