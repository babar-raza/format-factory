"""Tests for XCF product deepening sprint 173.

New functions:
  xcf_file_size_plus_width_plus_height  — size + width + height
  xcf_file_size_minus_width_times_2  — size - width*2, min 0
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_plus_width_plus_height,
    xcf_file_size_minus_width_times_2,
)

_RGB = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf")
_RGBA = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_GRAY = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf")


class TestXcfFileSizePlusWidthPlusHeight:
    def test_return_type(self):
        assert isinstance(xcf_file_size_plus_width_plus_height(_RGB), int)

    def test_exact_179_for_rgb(self):
        # 1x1-red-rgb: size=177, w=1, h=1 → 179
        assert xcf_file_size_plus_width_plus_height(_RGB) == 179

    def test_exact_180_for_rgba(self):
        # 1x1-rgba-blue: size=178, w=1, h=1 → 180
        assert xcf_file_size_plus_width_plus_height(_RGBA) == 180

    def test_exact_182_for_gray(self):
        # 2x2-gray: size=178, w=2, h=2 → 182
        assert xcf_file_size_plus_width_plus_height(_GRAY) == 182

    def test_positive(self):
        assert xcf_file_size_plus_width_plus_height(_RGB) > 0

    def test_consistent(self):
        assert xcf_file_size_plus_width_plus_height(_GRAY) == xcf_file_size_plus_width_plus_height(_GRAY)


class TestXcfFileSizeMinusWidthTimes2:
    def test_return_type(self):
        assert isinstance(xcf_file_size_minus_width_times_2(_RGB), int)

    def test_exact_175_for_rgb(self):
        # 1x1-red-rgb: size=177, w=1 → 177 - 2 = 175
        assert xcf_file_size_minus_width_times_2(_RGB) == 175

    def test_exact_176_for_rgba(self):
        # 1x1-rgba-blue: size=178, w=1 → 178 - 2 = 176
        assert xcf_file_size_minus_width_times_2(_RGBA) == 176

    def test_exact_174_for_gray(self):
        # 2x2-gray: size=178, w=2 → 178 - 4 = 174
        assert xcf_file_size_minus_width_times_2(_GRAY) == 174

    def test_nonnegative(self):
        assert xcf_file_size_minus_width_times_2(_RGB) >= 0

    def test_consistent(self):
        assert xcf_file_size_minus_width_times_2(_GRAY) == xcf_file_size_minus_width_times_2(_GRAY)
