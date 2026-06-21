"""Tests for XCF product deepening sprint 168.

New functions:
  xcf_file_size_plus_pixel_count — file size + pixel count (w*h)
  xcf_height_times_file_size     — canvas height * file size
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_plus_pixel_count,
    xcf_height_times_file_size,
)

_RGB = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf")
_RGBA = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_GRAY = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf")


class TestXcfFileSizePlusPixelCount:
    def test_return_type(self):
        assert isinstance(xcf_file_size_plus_pixel_count(_RGB), int)

    def test_exact_178_for_rgb(self):
        # 1x1-red-rgb: size=177, pixels=1*1=1 → 178
        assert xcf_file_size_plus_pixel_count(_RGB) == 178

    def test_exact_179_for_rgba(self):
        # 1x1-rgba-blue: size=178, pixels=1 → 179
        assert xcf_file_size_plus_pixel_count(_RGBA) == 179

    def test_exact_182_for_gray(self):
        # 2x2-gray: size=178, pixels=4 → 182
        assert xcf_file_size_plus_pixel_count(_GRAY) == 182

    def test_positive(self):
        assert xcf_file_size_plus_pixel_count(_RGB) > 0

    def test_consistent(self):
        assert xcf_file_size_plus_pixel_count(_GRAY) == xcf_file_size_plus_pixel_count(_GRAY)


class TestXcfHeightTimesFileSize:
    def test_return_type(self):
        assert isinstance(xcf_height_times_file_size(_RGB), int)

    def test_exact_177_for_rgb(self):
        # 1x1-red-rgb: h=1, size=177 → 177
        assert xcf_height_times_file_size(_RGB) == 177

    def test_exact_178_for_rgba(self):
        # 1x1-rgba-blue: h=1, size=178 → 178
        assert xcf_height_times_file_size(_RGBA) == 178

    def test_exact_356_for_gray(self):
        # 2x2-gray: h=2, size=178 → 356
        assert xcf_height_times_file_size(_GRAY) == 356

    def test_positive(self):
        assert xcf_height_times_file_size(_RGB) > 0

    def test_consistent(self):
        assert xcf_height_times_file_size(_GRAY) == xcf_height_times_file_size(_GRAY)
