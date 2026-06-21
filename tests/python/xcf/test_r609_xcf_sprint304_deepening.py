"""Sprint 304 XCF — 2 new analytics functions: mod17+layer_count and size*7+multi-dim."""
from __future__ import annotations
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO))

XCF_BLUE = REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"
XCF_RED = REPO / "samples/by-format/xcf/valid/1x1-red-rgb.xcf"
XCF_GRAY = REPO / "samples/by-format/xcf/valid/2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_17_times_150_plus_image_type_times_700_plus_width_times_height_times_250_plus_layer_count_times_400 as f1,
    xcf_file_size_times_7_plus_image_type_times_550_plus_width_times_120_plus_height_times_90_plus_layer_count_times_1100 as f2,
)


class TestXcfMod17Times150PlusImageTypeTimes700PlusWHTimes250PlusLayerTimes400:
    def test_blue_value(self):
        assert f1(XCF_BLUE) == 1850

    def test_red_value(self):
        assert f1(XCF_RED) == 1700

    def test_gray_value(self):
        assert f1(XCF_GRAY) == 3300

    def test_returns_int(self):
        assert isinstance(f1(XCF_BLUE), int)

    def test_nonnegative(self):
        assert f1(XCF_BLUE) >= 0

    def test_distinct_blue_red(self):
        assert f1(XCF_BLUE) != f1(XCF_RED)

    def test_distinct_blue_gray(self):
        assert f1(XCF_BLUE) != f1(XCF_GRAY)

    def test_distinct_red_gray(self):
        assert f1(XCF_RED) != f1(XCF_GRAY)

    def test_str_path(self):
        assert isinstance(f1(str(XCF_BLUE)), int)

    def test_exported(self):
        from src.python.xcf import xcf_file_size_mod_17_times_150_plus_image_type_times_700_plus_width_times_height_times_250_plus_layer_count_times_400 as fn
        assert fn(XCF_BLUE) == 1850


class TestXcfSizeTimes7PlusImageTypeTimes550PlusWidthTimes120PlusHeightTimes90PlusLayerTimes1100:
    def test_blue_value(self):
        assert f2(XCF_BLUE) == 2556

    def test_red_value(self):
        assert f2(XCF_RED) == 2549

    def test_gray_value(self):
        assert f2(XCF_GRAY) == 3316

    def test_returns_int(self):
        assert isinstance(f2(XCF_BLUE), int)

    def test_nonnegative(self):
        assert f2(XCF_BLUE) >= 0

    def test_distinct_blue_red(self):
        assert f2(XCF_BLUE) != f2(XCF_RED)

    def test_distinct_blue_gray(self):
        assert f2(XCF_BLUE) != f2(XCF_GRAY)

    def test_distinct_red_gray(self):
        assert f2(XCF_RED) != f2(XCF_GRAY)

    def test_str_path(self):
        assert isinstance(f2(str(XCF_BLUE)), int)

    def test_exported(self):
        from src.python.xcf import xcf_file_size_times_7_plus_image_type_times_550_plus_width_times_120_plus_height_times_90_plus_layer_count_times_1100 as fn
        assert fn(XCF_BLUE) == 2556
