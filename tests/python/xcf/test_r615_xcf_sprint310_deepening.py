"""Sprint 310 XCF product deepening — 2 new analytics functions, 20 tests.

Skill: add-python-api
Spec fact refs: FACT-XCF-EX-0003, FACT-XCF-EX-0004
"""
from __future__ import annotations

from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent.parent
_XCF_DIR = _REPO / "samples" / "by-format" / "xcf" / "valid"

XCF_BLUE = _XCF_DIR / "1x1-rgba-blue.xcf"
XCF_RED = _XCF_DIR / "1x1-red-rgb.xcf"
XCF_GRAY = _XCF_DIR / "2x2-gray.xcf"

import sys
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_23_times_250_plus_image_type_times_900_plus_width_times_height_times_400_plus_layer_count_times_1600 as f1,
    xcf_file_size_times_23_plus_image_type_times_650_plus_width_times_140_plus_height_times_120_plus_layer_count_times_1300 as f2,
)


class TestXcfFileSizeMod23Times250PlusImageType900PlusWidthHeight400PlusLayerCount1600:
    def test_blue_returns_int(self):
        assert isinstance(f1(XCF_BLUE), int)

    def test_blue_expected_value(self):
        assert f1(XCF_BLUE) == 6250

    def test_red_returns_int(self):
        assert isinstance(f1(XCF_RED), int)

    def test_red_expected_value(self):
        assert f1(XCF_RED) == 6000

    def test_gray_returns_int(self):
        assert isinstance(f1(XCF_GRAY), int)

    def test_gray_expected_value(self):
        assert f1(XCF_GRAY) == 8350

    def test_gray_greater_than_blue(self):
        assert f1(XCF_GRAY) > f1(XCF_BLUE)

    def test_blue_greater_than_red(self):
        assert f1(XCF_BLUE) > f1(XCF_RED)

    def test_path_string_accepted(self):
        assert isinstance(f1(str(XCF_BLUE)), int)

    def test_invalid_path_raises(self):
        with pytest.raises(Exception):
            f1("/nonexistent/path/missing.xcf")


class TestXcfFileSizeTimes23PlusImageType650PlusWidth140PlusHeight120PlusLayerCount1300:
    def test_blue_returns_int(self):
        assert isinstance(f2(XCF_BLUE), int)

    def test_blue_expected_value(self):
        assert f2(XCF_BLUE) == 5654

    def test_red_returns_int(self):
        assert isinstance(f2(XCF_RED), int)

    def test_red_expected_value(self):
        assert f2(XCF_RED) == 5631

    def test_gray_returns_int(self):
        assert isinstance(f2(XCF_GRAY), int)

    def test_gray_expected_value(self):
        assert f2(XCF_GRAY) == 6564

    def test_gray_greater_than_blue(self):
        assert f2(XCF_GRAY) > f2(XCF_BLUE)

    def test_blue_greater_than_red(self):
        assert f2(XCF_BLUE) > f2(XCF_RED)

    def test_path_string_accepted(self):
        assert isinstance(f2(str(XCF_GRAY)), int)

    def test_invalid_path_raises(self):
        with pytest.raises(Exception):
            f2("/nonexistent/path/missing.xcf")
