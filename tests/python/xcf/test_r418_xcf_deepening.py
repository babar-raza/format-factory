"""Tests for XCF product deepening sprint 189.

New functions:
  xcf_file_size_plus_width_times_height_times_10  — sz + w*h*10
  xcf_file_size_times_image_type_plus_2  — sz*(type+2)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_plus_width_times_height_times_10,
    xcf_file_size_times_image_type_plus_2,
)

_RED = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-red-rgb.xcf")
_BLUE = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf")
_GRAY = str(_REPO / "samples" / "by-format" / "xcf" / "valid" / "2x2-gray.xcf")


class TestXcfFileSizePlusWidthTimesHeightTimes10:
    def test_return_type(self):
        assert isinstance(xcf_file_size_plus_width_times_height_times_10(_RED), int)

    def test_exact_187_for_red(self):
        # 1x1-red: sz=177, w=1, h=1 → 177 + 1*1*10 = 187
        assert xcf_file_size_plus_width_times_height_times_10(_RED) == 187

    def test_exact_188_for_blue(self):
        # 1x1-rgba: sz=178, w=1, h=1 → 178 + 1*1*10 = 188
        assert xcf_file_size_plus_width_times_height_times_10(_BLUE) == 188

    def test_exact_218_for_gray(self):
        # 2x2-gray: sz=178, w=2, h=2 → 178 + 2*2*10 = 218
        assert xcf_file_size_plus_width_times_height_times_10(_GRAY) == 218

    def test_nonnegative(self):
        assert xcf_file_size_plus_width_times_height_times_10(_RED) >= 0

    def test_consistent(self):
        assert xcf_file_size_plus_width_times_height_times_10(_GRAY) == xcf_file_size_plus_width_times_height_times_10(_GRAY)


class TestXcfFileSizeTimesImageTypePlus2:
    def test_return_type(self):
        assert isinstance(xcf_file_size_times_image_type_plus_2(_RED), int)

    def test_exact_354_for_red(self):
        # 1x1-red: sz=177, type=0 → 177*(0+2) = 354
        assert xcf_file_size_times_image_type_plus_2(_RED) == 354

    def test_exact_356_for_blue(self):
        # 1x1-rgba: sz=178, type=0 → 178*(0+2) = 356
        assert xcf_file_size_times_image_type_plus_2(_BLUE) == 356

    def test_exact_534_for_gray(self):
        # 2x2-gray: sz=178, type=1 → 178*(1+2) = 534
        assert xcf_file_size_times_image_type_plus_2(_GRAY) == 534

    def test_nonnegative(self):
        assert xcf_file_size_times_image_type_plus_2(_RED) >= 0

    def test_consistent(self):
        assert xcf_file_size_times_image_type_plus_2(_GRAY) == xcf_file_size_times_image_type_plus_2(_GRAY)
