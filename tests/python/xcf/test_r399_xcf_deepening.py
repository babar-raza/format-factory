"""Tests for XCF product deepening sprint 170.

New functions:
  xcf_file_size_times_image_type_plus_one  — size * (type+1)
  xcf_file_size_minus_image_type_times_10  — size - type*10
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_times_image_type_plus_one,
    xcf_file_size_minus_image_type_times_10,
)

_RGB = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf")
_RGBA = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_GRAY = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf")


class TestXcfFileSizeTimesImageTypePlusOne:
    def test_return_type(self):
        assert isinstance(xcf_file_size_times_image_type_plus_one(_RGB), int)

    def test_exact_177_for_rgb(self):
        # 1x1-red-rgb: size=177, type=0 → 177*(0+1)=177
        assert xcf_file_size_times_image_type_plus_one(_RGB) == 177

    def test_exact_178_for_rgba(self):
        # 1x1-rgba-blue: size=178, type=0 → 178*(0+1)=178
        assert xcf_file_size_times_image_type_plus_one(_RGBA) == 178

    def test_exact_356_for_gray(self):
        # 2x2-gray: size=178, type=1 → 178*(1+1)=356
        assert xcf_file_size_times_image_type_plus_one(_GRAY) == 356

    def test_positive(self):
        assert xcf_file_size_times_image_type_plus_one(_RGB) > 0

    def test_consistent(self):
        assert xcf_file_size_times_image_type_plus_one(_GRAY) == xcf_file_size_times_image_type_plus_one(_GRAY)


class TestXcfFileSizeMinusImageTypeTimesTen:
    def test_return_type(self):
        assert isinstance(xcf_file_size_minus_image_type_times_10(_RGB), int)

    def test_exact_177_for_rgb(self):
        # 1x1-red-rgb: size=177, type=0 → 177-0=177
        assert xcf_file_size_minus_image_type_times_10(_RGB) == 177

    def test_exact_178_for_rgba(self):
        # 1x1-rgba-blue: size=178, type=0 → 178-0=178
        assert xcf_file_size_minus_image_type_times_10(_RGBA) == 178

    def test_exact_168_for_gray(self):
        # 2x2-gray: size=178, type=1 → 178-10=168
        assert xcf_file_size_minus_image_type_times_10(_GRAY) == 168

    def test_nonnegative(self):
        assert xcf_file_size_minus_image_type_times_10(_RGB) >= 0

    def test_consistent(self):
        assert xcf_file_size_minus_image_type_times_10(_GRAY) == xcf_file_size_minus_image_type_times_10(_GRAY)
