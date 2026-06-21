"""Tests for XCF product deepening sprint 192.

New functions:
  xcf_file_size_times_image_type_plus_1  — sz*(type+1)
  xcf_file_size_times_layers_plus_image_type_times_10_plus_dimensions  — sz*layers+type*10+w+h
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_times_image_type_plus_1,
    xcf_file_size_times_layers_plus_image_type_times_10_plus_dimensions,
)

_RED = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf")
_BLUE = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_GRAY = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf")


class TestXcfFileSizeTimesImageTypePlus1:
    def test_return_type(self):
        assert isinstance(xcf_file_size_times_image_type_plus_1(_RED), int)

    def test_exact_177_for_red(self):
        # 1x1-red: sz=177, type=0 → 177*(0+1) = 177
        assert xcf_file_size_times_image_type_plus_1(_RED) == 177

    def test_exact_178_for_blue(self):
        # 1x1-rgba: sz=178, type=0 → 178*(0+1) = 178
        assert xcf_file_size_times_image_type_plus_1(_BLUE) == 178

    def test_exact_356_for_gray(self):
        # 2x2-gray: sz=178, type=1 → 178*(1+1) = 356
        assert xcf_file_size_times_image_type_plus_1(_GRAY) == 356

    def test_nonnegative(self):
        assert xcf_file_size_times_image_type_plus_1(_RED) >= 0

    def test_consistent(self):
        assert xcf_file_size_times_image_type_plus_1(_GRAY) == xcf_file_size_times_image_type_plus_1(_GRAY)


class TestXcfFileSizeTimesLayersPlusImageTypeTimes10PlusDimensions:
    def test_return_type(self):
        assert isinstance(xcf_file_size_times_layers_plus_image_type_times_10_plus_dimensions(_RED), int)

    def test_exact_179_for_red(self):
        # 1x1-red: sz=177, layers=1, type=0, w=1, h=1 → 177*1 + 0*10 + 1 + 1 = 179
        assert xcf_file_size_times_layers_plus_image_type_times_10_plus_dimensions(_RED) == 179

    def test_exact_180_for_blue(self):
        # 1x1-rgba: sz=178, layers=1, type=0, w=1, h=1 → 178*1 + 0 + 1 + 1 = 180
        assert xcf_file_size_times_layers_plus_image_type_times_10_plus_dimensions(_BLUE) == 180

    def test_exact_192_for_gray(self):
        # 2x2-gray: sz=178, layers=1, type=1, w=2, h=2 → 178*1 + 1*10 + 2 + 2 = 192
        assert xcf_file_size_times_layers_plus_image_type_times_10_plus_dimensions(_GRAY) == 192

    def test_nonnegative(self):
        assert xcf_file_size_times_layers_plus_image_type_times_10_plus_dimensions(_RED) >= 0

    def test_consistent(self):
        assert xcf_file_size_times_layers_plus_image_type_times_10_plus_dimensions(_GRAY) == xcf_file_size_times_layers_plus_image_type_times_10_plus_dimensions(_GRAY)
