"""Tests for XCF product deepening sprint 155.

New functions:
  xcf_num_layers_plus_image_type_id — num_layers + image_type_id
  xcf_file_size_minus_width         — file size - canvas width
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import xcf_num_layers_plus_image_type_id, xcf_file_size_minus_width

_RGB = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf")
_RGBA = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_GRAY = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf")


class TestXcfNumLayersPlusImageTypeId:
    def test_return_type(self):
        assert isinstance(xcf_num_layers_plus_image_type_id(_RGB), int)

    def test_exact_1_for_rgb(self):
        # 1x1-red-rgb.xcf: 1 layer + 0 (RGB) = 1
        assert xcf_num_layers_plus_image_type_id(_RGB) == 1

    def test_exact_1_for_rgba(self):
        # 1x1-rgba-blue.xcf: 1 layer + 0 (RGB) = 1
        assert xcf_num_layers_plus_image_type_id(_RGBA) == 1

    def test_exact_2_for_gray(self):
        # 2x2-gray.xcf: 1 layer + 1 (GRAYSCALE) = 2
        assert xcf_num_layers_plus_image_type_id(_GRAY) == 2

    def test_positive(self):
        assert xcf_num_layers_plus_image_type_id(_RGB) >= 1

    def test_consistent(self):
        assert xcf_num_layers_plus_image_type_id(_GRAY) == xcf_num_layers_plus_image_type_id(_GRAY)


class TestXcfFileSizeMinusWidth:
    def test_return_type(self):
        assert isinstance(xcf_file_size_minus_width(_RGB), int)

    def test_exact_176_for_rgb(self):
        # 1x1-red-rgb.xcf: 177 bytes - 1 (width) = 176
        assert xcf_file_size_minus_width(_RGB) == 176

    def test_exact_177_for_rgba(self):
        # 1x1-rgba-blue.xcf: 178 bytes - 1 (width) = 177
        assert xcf_file_size_minus_width(_RGBA) == 177

    def test_exact_176_for_gray(self):
        # 2x2-gray.xcf: 178 bytes - 2 (width) = 176
        assert xcf_file_size_minus_width(_GRAY) == 176

    def test_positive(self):
        assert xcf_file_size_minus_width(_RGB) > 0

    def test_consistent(self):
        assert xcf_file_size_minus_width(_RGB) == xcf_file_size_minus_width(_RGB)
