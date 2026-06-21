"""Tests for XCF product deepening sprint 186.

New functions:
  xcf_file_size_plus_num_layers_times_width  — sz + layers*w
  xcf_file_size_times_num_layers_plus_width_times_height  — sz*layers + w*h
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_plus_num_layers_times_width,
    xcf_file_size_times_num_layers_plus_width_times_height,
)

_RED = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf")
_BLUE = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_GRAY = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf")


class TestXcfFileSizePlusNumLayersTimesWidth:
    def test_return_type(self):
        assert isinstance(xcf_file_size_plus_num_layers_times_width(_RED), int)

    def test_exact_178_for_red(self):
        # 1x1-red: sz=177, layers=1, w=1 → 177 + 1*1 = 178
        assert xcf_file_size_plus_num_layers_times_width(_RED) == 178

    def test_exact_179_for_blue(self):
        # 1x1-rgba: sz=178, layers=1, w=1 → 178 + 1*1 = 179
        assert xcf_file_size_plus_num_layers_times_width(_BLUE) == 179

    def test_exact_180_for_gray(self):
        # 2x2-gray: sz=178, layers=1, w=2 → 178 + 1*2 = 180
        assert xcf_file_size_plus_num_layers_times_width(_GRAY) == 180

    def test_nonnegative(self):
        assert xcf_file_size_plus_num_layers_times_width(_RED) >= 0

    def test_consistent(self):
        assert xcf_file_size_plus_num_layers_times_width(_GRAY) == xcf_file_size_plus_num_layers_times_width(_GRAY)


class TestXcfFileSizeTimesNumLayersPlusWidthTimesHeight:
    def test_return_type(self):
        assert isinstance(xcf_file_size_times_num_layers_plus_width_times_height(_RED), int)

    def test_exact_178_for_red(self):
        # 1x1-red: sz=177, layers=1, w=1, h=1 → 177*1 + 1*1 = 178
        assert xcf_file_size_times_num_layers_plus_width_times_height(_RED) == 178

    def test_exact_179_for_blue(self):
        # 1x1-rgba: sz=178, layers=1, w=1, h=1 → 178*1 + 1*1 = 179
        assert xcf_file_size_times_num_layers_plus_width_times_height(_BLUE) == 179

    def test_exact_182_for_gray(self):
        # 2x2-gray: sz=178, layers=1, w=2, h=2 → 178*1 + 2*2 = 182
        assert xcf_file_size_times_num_layers_plus_width_times_height(_GRAY) == 182

    def test_nonnegative(self):
        assert xcf_file_size_times_num_layers_plus_width_times_height(_RED) >= 0

    def test_consistent(self):
        assert xcf_file_size_times_num_layers_plus_width_times_height(_GRAY) == xcf_file_size_times_num_layers_plus_width_times_height(_GRAY)
