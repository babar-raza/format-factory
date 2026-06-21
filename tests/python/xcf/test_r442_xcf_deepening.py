"""Sprint 213 XCF deepening — 2 new analytics functions, 12 tests.

Functions:
  xcf_file_size_plus_width_times_image_type_plus_height_times_layers
  xcf_file_size_mod_50_plus_width_times_height_times_layers

Samples (samples/by-format/xcf/valid/):
  1x1-red-rgb.xcf   sz=177, type=0, w=1, h=1, layers=1
  1x1-rgba-blue.xcf sz=178, type=0, w=1, h=1, layers=1
  2x2-gray.xcf      sz=178, type=1, w=2, h=2, layers=1

Expected:
  xcf_file_size_plus_width_times_image_type_plus_height_times_layers:
    red  = 177 + 1*0 + 1*1 = 178
    blue = 178 + 1*0 + 1*1 = 179
    gray = 178 + 2*1 + 2*1 = 182

  xcf_file_size_mod_50_plus_width_times_height_times_layers:
    red  = 177%50 + 1*1*1 = 28
    blue = 178%50 + 1*1*1 = 29
    gray = 178%50 + 2*2*1 = 32
"""
from pathlib import Path

import pytest

from src.python.xcf import (
    xcf_file_size_plus_width_times_image_type_plus_height_times_layers,
    xcf_file_size_mod_50_plus_width_times_height_times_layers,
)

_VALID = Path("samples/by-format/xcf/valid")
RED = _VALID / "1x1-red-rgb.xcf"
BLUE = _VALID / "1x1-rgba-blue.xcf"
GRAY = _VALID / "2x2-gray.xcf"


class TestXcfFileSizePlusWidthTimesImageTypePlusHeightTimesLayers:
    def test_red_value(self):
        assert xcf_file_size_plus_width_times_image_type_plus_height_times_layers(RED) == 178

    def test_blue_value(self):
        assert xcf_file_size_plus_width_times_image_type_plus_height_times_layers(BLUE) == 179

    def test_gray_value(self):
        assert xcf_file_size_plus_width_times_image_type_plus_height_times_layers(GRAY) == 182

    def test_returns_int(self):
        assert isinstance(xcf_file_size_plus_width_times_image_type_plus_height_times_layers(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_plus_width_times_image_type_plus_height_times_layers(RED),
            xcf_file_size_plus_width_times_image_type_plus_height_times_layers(BLUE),
            xcf_file_size_plus_width_times_image_type_plus_height_times_layers(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_plus_width_times_image_type_plus_height_times_layers(RED) > 0


class TestXcfFileSizeMod50PlusWidthTimesHeightTimesLayers:
    def test_red_value(self):
        assert xcf_file_size_mod_50_plus_width_times_height_times_layers(RED) == 28

    def test_blue_value(self):
        assert xcf_file_size_mod_50_plus_width_times_height_times_layers(BLUE) == 29

    def test_gray_value(self):
        assert xcf_file_size_mod_50_plus_width_times_height_times_layers(GRAY) == 32

    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_50_plus_width_times_height_times_layers(RED), int)

    def test_all_distinct(self):
        vals = [
            xcf_file_size_mod_50_plus_width_times_height_times_layers(RED),
            xcf_file_size_mod_50_plus_width_times_height_times_layers(BLUE),
            xcf_file_size_mod_50_plus_width_times_height_times_layers(GRAY),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert xcf_file_size_mod_50_plus_width_times_height_times_layers(RED) > 0
