"""Tests for XCF product deepening sprint 195.

New functions:
  xcf_file_size_div_image_type_plus_1  — sz//(type+1)
  xcf_file_size_plus_width_plus_height_times_layers_times_5  — sz+(w+h)*layers*5
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_div_image_type_plus_1,
    xcf_file_size_plus_width_plus_height_times_layers_times_5,
)

_RED = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf")
_BLUE = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_GRAY = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf")


class TestXcfFileSizeDivImageTypePlus1:
    def test_return_type(self):
        assert isinstance(xcf_file_size_div_image_type_plus_1(_RED), int)

    def test_exact_177_for_red(self):
        # 1x1-red: sz=177, type=0 → 177//(0+1) = 177
        assert xcf_file_size_div_image_type_plus_1(_RED) == 177

    def test_exact_178_for_blue(self):
        # 1x1-rgba: sz=178, type=0 → 178//(0+1) = 178
        assert xcf_file_size_div_image_type_plus_1(_BLUE) == 178

    def test_exact_89_for_gray(self):
        # 2x2-gray: sz=178, type=1 → 178//(1+1) = 89
        assert xcf_file_size_div_image_type_plus_1(_GRAY) == 89

    def test_nonnegative(self):
        assert xcf_file_size_div_image_type_plus_1(_RED) >= 0

    def test_consistent(self):
        assert xcf_file_size_div_image_type_plus_1(_GRAY) == xcf_file_size_div_image_type_plus_1(_GRAY)


class TestXcfFileSizePlusWidthPlusHeightTimesLayersTimes5:
    def test_return_type(self):
        assert isinstance(xcf_file_size_plus_width_plus_height_times_layers_times_5(_RED), int)

    def test_exact_187_for_red(self):
        # 1x1-red: sz=177, w=1, h=1, layers=1 → 177 + (1+1)*1*5 = 187
        assert xcf_file_size_plus_width_plus_height_times_layers_times_5(_RED) == 187

    def test_exact_188_for_blue(self):
        # 1x1-rgba: sz=178, w=1, h=1, layers=1 → 178 + (1+1)*1*5 = 188
        assert xcf_file_size_plus_width_plus_height_times_layers_times_5(_BLUE) == 188

    def test_exact_198_for_gray(self):
        # 2x2-gray: sz=178, w=2, h=2, layers=1 → 178 + (2+2)*1*5 = 198
        assert xcf_file_size_plus_width_plus_height_times_layers_times_5(_GRAY) == 198

    def test_nonnegative(self):
        assert xcf_file_size_plus_width_plus_height_times_layers_times_5(_RED) >= 0

    def test_consistent(self):
        assert xcf_file_size_plus_width_plus_height_times_layers_times_5(_GRAY) == xcf_file_size_plus_width_plus_height_times_layers_times_5(_GRAY)
