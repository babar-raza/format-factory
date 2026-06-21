"""Tests for XCF product deepening sprint 158.

New functions:
  xcf_file_size_plus_image_type_id  — file size + image type id (0/1/2)
  xcf_width_times_file_size         — canvas width * file size in bytes
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_plus_image_type_id,
    xcf_width_times_file_size,
)

_RGB = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf")
_RGBA = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_GRAY = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf")


class TestXcfFileSizePlusImageTypeId:
    def test_return_type(self):
        assert isinstance(xcf_file_size_plus_image_type_id(_RGB), int)

    def test_exact_177_for_rgb(self):
        # 1x1-red-rgb: size=177, type=0 → 177
        assert xcf_file_size_plus_image_type_id(_RGB) == 177

    def test_exact_178_for_rgba(self):
        # 1x1-rgba-blue: size=178, type=0 → 178
        assert xcf_file_size_plus_image_type_id(_RGBA) == 178

    def test_exact_179_for_gray(self):
        # 2x2-gray: size=178, type=1 → 179
        assert xcf_file_size_plus_image_type_id(_GRAY) == 179

    def test_positive(self):
        assert xcf_file_size_plus_image_type_id(_RGB) > 0

    def test_consistent(self):
        assert xcf_file_size_plus_image_type_id(_GRAY) == xcf_file_size_plus_image_type_id(_GRAY)


class TestXcfWidthTimesFileSize:
    def test_return_type(self):
        assert isinstance(xcf_width_times_file_size(_RGB), int)

    def test_exact_177_for_rgb(self):
        # 1x1-red-rgb: w=1, size=177 → 177
        assert xcf_width_times_file_size(_RGB) == 177

    def test_exact_178_for_rgba(self):
        # 1x1-rgba-blue: w=1, size=178 → 178
        assert xcf_width_times_file_size(_RGBA) == 178

    def test_exact_356_for_gray(self):
        # 2x2-gray: w=2, size=178 → 356
        assert xcf_width_times_file_size(_GRAY) == 356

    def test_positive(self):
        assert xcf_width_times_file_size(_RGB) > 0

    def test_consistent(self):
        assert xcf_width_times_file_size(_GRAY) == xcf_width_times_file_size(_GRAY)
