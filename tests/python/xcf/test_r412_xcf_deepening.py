"""Tests for XCF product deepening sprint 183.

New functions:
  xcf_height_squared_plus_file_size  — height*height + size
  xcf_num_layers_times_file_size_plus_image_type_times_10  — layers*size + type*10
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_height_squared_plus_file_size,
    xcf_num_layers_times_file_size_plus_image_type_times_10,
)

_RGB = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf")
_RGBA = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_GRAY = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf")


class TestXcfHeightSquaredPlusFileSize:
    def test_return_type(self):
        assert isinstance(xcf_height_squared_plus_file_size(_RGB), int)

    def test_exact_178_for_rgb(self):
        # 1x1-red-rgb: h=1, size=177 → 1*1 + 177 = 178
        assert xcf_height_squared_plus_file_size(_RGB) == 178

    def test_exact_179_for_rgba(self):
        # 1x1-rgba-blue: h=1, size=178 → 1*1 + 178 = 179
        assert xcf_height_squared_plus_file_size(_RGBA) == 179

    def test_exact_182_for_gray(self):
        # 2x2-gray: h=2, size=178 → 2*2 + 178 = 182
        assert xcf_height_squared_plus_file_size(_GRAY) == 182

    def test_positive(self):
        assert xcf_height_squared_plus_file_size(_RGB) > 0

    def test_consistent(self):
        assert xcf_height_squared_plus_file_size(_GRAY) == xcf_height_squared_plus_file_size(_GRAY)


class TestXcfNumLayersTimesFileSizePlusImageTypeTimes10:
    def test_return_type(self):
        assert isinstance(xcf_num_layers_times_file_size_plus_image_type_times_10(_RGB), int)

    def test_exact_177_for_rgb(self):
        # 1x1-red-rgb: layers=1, size=177, type=0 → 1*177 + 0*10 = 177
        assert xcf_num_layers_times_file_size_plus_image_type_times_10(_RGB) == 177

    def test_exact_178_for_rgba(self):
        # 1x1-rgba-blue: layers=1, size=178, type=0 → 1*178 + 0*10 = 178
        assert xcf_num_layers_times_file_size_plus_image_type_times_10(_RGBA) == 178

    def test_exact_188_for_gray(self):
        # 2x2-gray: layers=1, size=178, type=1 → 1*178 + 1*10 = 188
        assert xcf_num_layers_times_file_size_plus_image_type_times_10(_GRAY) == 188

    def test_positive(self):
        assert xcf_num_layers_times_file_size_plus_image_type_times_10(_RGB) > 0

    def test_consistent(self):
        assert xcf_num_layers_times_file_size_plus_image_type_times_10(_GRAY) == xcf_num_layers_times_file_size_plus_image_type_times_10(_GRAY)
