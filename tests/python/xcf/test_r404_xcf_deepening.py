"""Tests for XCF product deepening sprint 175.

New functions:
  xcf_file_size_plus_image_type_times_100  — size + type*100
  xcf_file_size_minus_height_times_10  — size - height*10, min 0
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_plus_image_type_times_100,
    xcf_file_size_minus_height_times_10,
)

_RGB = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf")
_RGBA = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_GRAY = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf")


class TestXcfFileSizePlusImageTypeTimesHundred:
    def test_return_type(self):
        assert isinstance(xcf_file_size_plus_image_type_times_100(_RGB), int)

    def test_exact_177_for_rgb(self):
        # 1x1-red-rgb: size=177, type=0 → 177 + 0 = 177
        assert xcf_file_size_plus_image_type_times_100(_RGB) == 177

    def test_exact_178_for_rgba(self):
        # 1x1-rgba-blue: size=178, type=0 → 178 + 0 = 178
        assert xcf_file_size_plus_image_type_times_100(_RGBA) == 178

    def test_exact_278_for_gray(self):
        # 2x2-gray: size=178, type=1 → 178 + 100 = 278
        assert xcf_file_size_plus_image_type_times_100(_GRAY) == 278

    def test_positive(self):
        assert xcf_file_size_plus_image_type_times_100(_RGB) > 0

    def test_consistent(self):
        assert xcf_file_size_plus_image_type_times_100(_GRAY) == xcf_file_size_plus_image_type_times_100(_GRAY)


class TestXcfFileSizeMinusHeightTimes10:
    def test_return_type(self):
        assert isinstance(xcf_file_size_minus_height_times_10(_RGB), int)

    def test_exact_167_for_rgb(self):
        # 1x1-red-rgb: size=177, h=1 → 177 - 10 = 167
        assert xcf_file_size_minus_height_times_10(_RGB) == 167

    def test_exact_168_for_rgba(self):
        # 1x1-rgba-blue: size=178, h=1 → 178 - 10 = 168
        assert xcf_file_size_minus_height_times_10(_RGBA) == 168

    def test_exact_158_for_gray(self):
        # 2x2-gray: size=178, h=2 → 178 - 20 = 158
        assert xcf_file_size_minus_height_times_10(_GRAY) == 158

    def test_nonnegative(self):
        assert xcf_file_size_minus_height_times_10(_RGB) >= 0

    def test_consistent(self):
        assert xcf_file_size_minus_height_times_10(_GRAY) == xcf_file_size_minus_height_times_10(_GRAY)
