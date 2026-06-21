"""Tests for XCF product deepening sprint 148.

New functions:
  xcf_image_type_id        — raw image_type field (0=RGB, 1=GRAYSCALE, 2=INDEXED)
  xcf_file_size_minus_header — file size minus 26-byte XCF header
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_image_type_id, xcf_file_size_minus_header

_RGB = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf")
_RGBA = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_GRAY = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf")


class TestXcfImageTypeId:
    def test_return_type(self):
        assert isinstance(xcf_image_type_id(_RGB), int)

    def test_zero_for_rgb(self):
        # 1x1-red-rgb.xcf: image_type = 0 (RGB)
        assert xcf_image_type_id(_RGB) == 0

    def test_zero_for_rgba(self):
        # 1x1-rgba-blue.xcf: image_type = 0 (RGB, alpha is a layer property)
        assert xcf_image_type_id(_RGBA) == 0

    def test_one_for_grayscale(self):
        # 2x2-gray.xcf: image_type = 1 (GRAYSCALE)
        assert xcf_image_type_id(_GRAY) == 1

    def test_nonnegative(self):
        assert xcf_image_type_id(_RGB) >= 0

    def test_consistent(self):
        assert xcf_image_type_id(_GRAY) == xcf_image_type_id(_GRAY)


class TestXcfFileSizeMinusHeader:
    def test_return_type(self):
        assert isinstance(xcf_file_size_minus_header(_RGB), int)

    def test_exact_151_for_red_rgb(self):
        # 1x1-red-rgb.xcf: 177 bytes - 26 header = 151
        assert xcf_file_size_minus_header(_RGB) == 151

    def test_exact_152_for_rgba(self):
        # 1x1-rgba-blue.xcf: 178 bytes - 26 header = 152
        assert xcf_file_size_minus_header(_RGBA) == 152

    def test_exact_152_for_gray(self):
        # 2x2-gray.xcf: 178 bytes - 26 header = 152
        assert xcf_file_size_minus_header(_GRAY) == 152

    def test_nonnegative(self):
        assert xcf_file_size_minus_header(_RGB) >= 0

    def test_consistent(self):
        assert xcf_file_size_minus_header(_RGB) == xcf_file_size_minus_header(_RGB)
