"""Sprint 249 XCF analytics deepening tests.

Functions:
- xcf_file_size_mod_11_times_150_plus_image_type_times_800_plus_width_times_height_times_200
- xcf_file_size_mod_7_times_200_plus_image_type_times_500_plus_width_plus_height_times_100
"""
import pytest
from pathlib import Path

REPO = Path(__file__).parent.parent.parent.parent
XCF = REPO / "samples/by-format/xcf/valid"
RED = XCF / "1x1-red-rgb.xcf"    # fs=177, type=0, w=1, h=1, layers=1
BLUE = XCF / "1x1-rgba-blue.xcf"  # fs=178, type=0, w=1, h=1, layers=1
GRAY = XCF / "2x2-gray.xcf"       # fs=178, type=1, w=2, h=2, layers=1

from src.python.xcf import (
    xcf_file_size_mod_11_times_150_plus_image_type_times_800_plus_width_times_height_times_200 as f1,
    xcf_file_size_mod_7_times_200_plus_image_type_times_500_plus_width_plus_height_times_100 as f2,
)


class TestXcfFileSizeMod11Times150PlusImageTypeTimes800PlusWidthTimesHeightTimes200:
    def test_red(self):
        assert f1(RED) == 350

    def test_blue(self):
        assert f1(BLUE) == 500

    def test_gray(self):
        assert f1(GRAY) == 1900

    def test_returns_int(self):
        assert isinstance(f1(RED), int)

    def test_nonnegative(self):
        assert f1(RED) >= 0

    def test_distinct_red_blue(self):
        assert f1(RED) != f1(BLUE)

    def test_distinct_blue_gray(self):
        assert f1(BLUE) != f1(GRAY)

    def test_gray_largest(self):
        assert f1(GRAY) > f1(BLUE)

    def test_blue_larger_than_red(self):
        assert f1(BLUE) > f1(RED)

    def test_path_object(self):
        assert f1(Path(RED)) == 350


class TestXcfFileSizeMod7Times200PlusImageTypeTimes500PlusWidthPlusHeightTimes100:
    def test_red(self):
        assert f2(RED) == 600

    def test_blue(self):
        assert f2(BLUE) == 800

    def test_gray(self):
        assert f2(GRAY) == 1500

    def test_returns_int(self):
        assert isinstance(f2(RED), int)

    def test_nonnegative(self):
        assert f2(RED) >= 0

    def test_distinct_red_blue(self):
        assert f2(RED) != f2(BLUE)

    def test_distinct_blue_gray(self):
        assert f2(BLUE) != f2(GRAY)

    def test_gray_largest(self):
        assert f2(GRAY) > f2(BLUE)

    def test_blue_larger_than_red(self):
        assert f2(BLUE) > f2(RED)

    def test_path_object(self):
        assert f2(Path(RED)) == 600
