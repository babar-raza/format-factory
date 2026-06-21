"""Tests for XCF product deepening sprint 180.

New functions:
  xcf_file_size_minus_image_type_times_50  — size - type*50, min 0
  xcf_width_squared_plus_file_size  — width*width + size
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_minus_image_type_times_50,
    xcf_width_squared_plus_file_size,
)

_RGB = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf")
_RGBA = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_GRAY = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf")


class TestXcfFileSizeMinusImageTypeTimes50:
    def test_return_type(self):
        assert isinstance(xcf_file_size_minus_image_type_times_50(_RGB), int)

    def test_exact_177_for_rgb(self):
        # 1x1-red-rgb: size=177, type=0 → 177 - 0 = 177
        assert xcf_file_size_minus_image_type_times_50(_RGB) == 177

    def test_exact_178_for_rgba(self):
        # 1x1-rgba-blue: size=178, type=0 → 178 - 0 = 178
        assert xcf_file_size_minus_image_type_times_50(_RGBA) == 178

    def test_exact_128_for_gray(self):
        # 2x2-gray: size=178, type=1 → 178 - 50 = 128
        assert xcf_file_size_minus_image_type_times_50(_GRAY) == 128

    def test_nonnegative(self):
        assert xcf_file_size_minus_image_type_times_50(_RGB) >= 0

    def test_consistent(self):
        assert xcf_file_size_minus_image_type_times_50(_GRAY) == xcf_file_size_minus_image_type_times_50(_GRAY)


class TestXcfWidthSquaredPlusFileSize:
    def test_return_type(self):
        assert isinstance(xcf_width_squared_plus_file_size(_RGB), int)

    def test_exact_178_for_rgb(self):
        # 1x1-red-rgb: w=1, size=177 → 1*1 + 177 = 178
        assert xcf_width_squared_plus_file_size(_RGB) == 178

    def test_exact_179_for_rgba(self):
        # 1x1-rgba-blue: w=1, size=178 → 1*1 + 178 = 179
        assert xcf_width_squared_plus_file_size(_RGBA) == 179

    def test_exact_182_for_gray(self):
        # 2x2-gray: w=2, size=178 → 2*2 + 178 = 182
        assert xcf_width_squared_plus_file_size(_GRAY) == 182

    def test_positive(self):
        assert xcf_width_squared_plus_file_size(_RGB) > 0

    def test_consistent(self):
        assert xcf_width_squared_plus_file_size(_GRAY) == xcf_width_squared_plus_file_size(_GRAY)
