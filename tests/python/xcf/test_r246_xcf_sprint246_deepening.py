"""Sprint 246 XCF analytics deepening tests.

Functions:
- xcf_file_size_mod_13_times_150_plus_image_type_times_600_plus_width_times_height_times_100
- xcf_file_size_mod_7_plus_image_type_times_400_plus_width_times_height_times_num_layers_times_300
"""
import pytest
from pathlib import Path

REPO = Path(__file__).parent.parent.parent.parent
XCF_VALID = REPO / "samples/by-format/xcf/valid"
RED = XCF_VALID / "1x1-red-rgb.xcf"
BLUE = XCF_VALID / "1x1-rgba-blue.xcf"
GRAY = XCF_VALID / "2x2-gray.xcf"

from src.python.xcf import (
    xcf_file_size_mod_13_times_150_plus_image_type_times_600_plus_width_times_height_times_100 as f1,
    xcf_file_size_mod_7_plus_image_type_times_400_plus_width_times_height_times_num_layers_times_300 as f2,
)


class TestXcfFileSizeMod13Times150PlusImageTypeTimes600PlusWidthTimesHeightTimes100:
    def test_red_rgb(self):
        assert f1(RED) == 1300

    def test_rgba_blue(self):
        assert f1(BLUE) == 1450

    def test_gray_2x2(self):
        assert f1(GRAY) == 2350

    def test_returns_int(self):
        assert isinstance(f1(RED), int)

    def test_nonnegative(self):
        assert f1(RED) >= 0

    def test_distinct_red_blue(self):
        assert f1(RED) != f1(BLUE)

    def test_distinct_blue_gray(self):
        assert f1(BLUE) != f1(GRAY)

    def test_gray_larger_than_red(self):
        assert f1(GRAY) > f1(RED)

    def test_gray_larger_than_blue(self):
        assert f1(GRAY) > f1(BLUE)

    def test_path_object(self):
        assert f1(Path(RED)) == 1300


class TestXcfFileSizeMod7PlusImageTypeTimes400PlusWidthTimesHeightTimesNumLayersTimes300:
    def test_red_rgb(self):
        assert f2(RED) == 302

    def test_rgba_blue(self):
        assert f2(BLUE) == 303

    def test_gray_2x2(self):
        assert f2(GRAY) == 1603

    def test_returns_int(self):
        assert isinstance(f2(RED), int)

    def test_nonnegative(self):
        assert f2(RED) >= 0

    def test_distinct_red_blue(self):
        assert f2(RED) != f2(BLUE)

    def test_distinct_blue_gray(self):
        assert f2(BLUE) != f2(GRAY)

    def test_gray_larger_than_blue(self):
        assert f2(GRAY) > f2(BLUE)

    def test_gray_larger_than_red(self):
        assert f2(GRAY) > f2(RED)

    def test_path_object(self):
        assert f2(Path(RED)) == 302
