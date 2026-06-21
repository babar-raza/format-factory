"""Sprint 525 - XCF deepening: 2 compound analytics functions, 20 tests.

skill_id: /add-analytics-function
format_id: xcf
target: src/python/xcf/xcf_analytics.py
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_883_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040,
    xcf_file_size_times_193_plus_image_type_times_12400_plus_width_times_height_times_7400,
)

_SAMPLE_RED = _REPO / "samples/by-format/xcf/valid/1x1-red-rgb.xcf"
_SAMPLE_BLUE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"
_SAMPLE_GRAY = _REPO / "samples/by-format/xcf/valid/2x2-gray.xcf"

FN1_RED = 1577410
FN1_BLUE = 1586310
FN1_GRAY = 1599220

FN2_RED = 41561
FN2_BLUE = 41754
FN2_GRAY = 76354


class TestXcfFileSizeMod883Times8900PlusImageTypeTimes10800PlusWidthTimes1070PlusHeightTimes1040:
    def test_returns_int_red(self):
        assert isinstance(
            xcf_file_size_mod_883_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040(_SAMPLE_RED),
            int,
        )

    def test_returns_int_blue(self):
        assert isinstance(
            xcf_file_size_mod_883_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040(_SAMPLE_BLUE),
            int,
        )

    def test_returns_int_gray(self):
        assert isinstance(
            xcf_file_size_mod_883_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040(_SAMPLE_GRAY),
            int,
        )

    def test_expected_red(self):
        assert xcf_file_size_mod_883_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040(_SAMPLE_RED) == FN1_RED

    def test_expected_blue(self):
        assert xcf_file_size_mod_883_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040(_SAMPLE_BLUE) == FN1_BLUE

    def test_expected_gray(self):
        assert xcf_file_size_mod_883_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040(_SAMPLE_GRAY) == FN1_GRAY

    def test_positive_result_red(self):
        assert xcf_file_size_mod_883_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040(_SAMPLE_RED) > 0

    def test_positive_result_gray(self):
        assert xcf_file_size_mod_883_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040(_SAMPLE_GRAY) > 0

    def test_red_differs_from_blue(self):
        r1 = xcf_file_size_mod_883_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040(_SAMPLE_RED)
        r2 = xcf_file_size_mod_883_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040(_SAMPLE_BLUE)
        assert r1 != r2

    def test_gray_differs_from_red(self):
        r1 = xcf_file_size_mod_883_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040(_SAMPLE_GRAY)
        r2 = xcf_file_size_mod_883_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040(_SAMPLE_RED)
        assert r1 != r2


class TestXcfFileSizeTimes193PlusImageTypeTimes12400PlusWidthTimesHeightTimes7400:
    def test_returns_int_red(self):
        assert isinstance(
            xcf_file_size_times_193_plus_image_type_times_12400_plus_width_times_height_times_7400(_SAMPLE_RED),
            int,
        )

    def test_returns_int_blue(self):
        assert isinstance(
            xcf_file_size_times_193_plus_image_type_times_12400_plus_width_times_height_times_7400(_SAMPLE_BLUE),
            int,
        )

    def test_returns_int_gray(self):
        assert isinstance(
            xcf_file_size_times_193_plus_image_type_times_12400_plus_width_times_height_times_7400(_SAMPLE_GRAY),
            int,
        )

    def test_expected_red(self):
        assert xcf_file_size_times_193_plus_image_type_times_12400_plus_width_times_height_times_7400(_SAMPLE_RED) == FN2_RED

    def test_expected_blue(self):
        assert xcf_file_size_times_193_plus_image_type_times_12400_plus_width_times_height_times_7400(_SAMPLE_BLUE) == FN2_BLUE

    def test_expected_gray(self):
        assert xcf_file_size_times_193_plus_image_type_times_12400_plus_width_times_height_times_7400(_SAMPLE_GRAY) == FN2_GRAY

    def test_positive_result_red(self):
        assert xcf_file_size_times_193_plus_image_type_times_12400_plus_width_times_height_times_7400(_SAMPLE_RED) > 0

    def test_positive_result_gray(self):
        assert xcf_file_size_times_193_plus_image_type_times_12400_plus_width_times_height_times_7400(_SAMPLE_GRAY) > 0

    def test_red_differs_from_blue(self):
        r1 = xcf_file_size_times_193_plus_image_type_times_12400_plus_width_times_height_times_7400(_SAMPLE_RED)
        r2 = xcf_file_size_times_193_plus_image_type_times_12400_plus_width_times_height_times_7400(_SAMPLE_BLUE)
        assert r1 != r2

    def test_gray_differs_from_red(self):
        r1 = xcf_file_size_times_193_plus_image_type_times_12400_plus_width_times_height_times_7400(_SAMPLE_GRAY)
        r2 = xcf_file_size_times_193_plus_image_type_times_12400_plus_width_times_height_times_7400(_SAMPLE_RED)
        assert r1 != r2
