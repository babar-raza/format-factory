"""Tests for XCF product deepening sprint 177.

New functions:
  xcf_file_size_times_width_plus_image_type  — size*width + type
  xcf_file_size_plus_height_times_image_type_plus_one  — size + height*(type+1)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_times_width_plus_image_type,
    xcf_file_size_plus_height_times_image_type_plus_one,
)

_RGB = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf")
_RGBA = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_GRAY = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf")


class TestXcfFileSizeTimesWidthPlusImageType:
    def test_return_type(self):
        assert isinstance(xcf_file_size_times_width_plus_image_type(_RGB), int)

    def test_exact_177_for_rgb(self):
        # 1x1-red-rgb: size=177, w=1, type=0 → 177*1+0 = 177
        assert xcf_file_size_times_width_plus_image_type(_RGB) == 177

    def test_exact_178_for_rgba(self):
        # 1x1-rgba-blue: size=178, w=1, type=0 → 178*1+0 = 178
        assert xcf_file_size_times_width_plus_image_type(_RGBA) == 178

    def test_exact_357_for_gray(self):
        # 2x2-gray: size=178, w=2, type=1 → 178*2+1 = 357
        assert xcf_file_size_times_width_plus_image_type(_GRAY) == 357

    def test_positive(self):
        assert xcf_file_size_times_width_plus_image_type(_RGB) > 0

    def test_consistent(self):
        assert xcf_file_size_times_width_plus_image_type(_GRAY) == xcf_file_size_times_width_plus_image_type(_GRAY)


class TestXcfFileSizePlusHeightTimesImageTypePlusOne:
    def test_return_type(self):
        assert isinstance(xcf_file_size_plus_height_times_image_type_plus_one(_RGB), int)

    def test_exact_178_for_rgb(self):
        # 1x1-red-rgb: size=177, h=1, type=0 → 177 + 1*(0+1) = 178
        assert xcf_file_size_plus_height_times_image_type_plus_one(_RGB) == 178

    def test_exact_179_for_rgba(self):
        # 1x1-rgba-blue: size=178, h=1, type=0 → 178 + 1*(0+1) = 179
        assert xcf_file_size_plus_height_times_image_type_plus_one(_RGBA) == 179

    def test_exact_182_for_gray(self):
        # 2x2-gray: size=178, h=2, type=1 → 178 + 2*(1+1) = 182
        assert xcf_file_size_plus_height_times_image_type_plus_one(_GRAY) == 182

    def test_positive(self):
        assert xcf_file_size_plus_height_times_image_type_plus_one(_RGB) > 0

    def test_consistent(self):
        assert xcf_file_size_plus_height_times_image_type_plus_one(_GRAY) == xcf_file_size_plus_height_times_image_type_plus_one(_GRAY)
