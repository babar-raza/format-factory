"""Sprint R850 — XCF compound analytics deepening tests (Sprint 297)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_103_times_1800_plus_image_type_times_2100_plus_width_times_200_plus_height_times_170,
    xcf_file_size_times_23_plus_image_type_times_2400_plus_width_times_height_times_800,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod103Times1800PlusImageTypeTimes2100PlusWidthTimes200PlusHeightTimes170:
    def test_returns_int(self):
        result = xcf_file_size_mod_103_times_1800_plus_image_type_times_2100_plus_width_times_200_plus_height_times_170(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_103_times_1800_plus_image_type_times_2100_plus_width_times_200_plus_height_times_170(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_103_times_1800_plus_image_type_times_2100_plus_width_times_200_plus_height_times_170(_XCF)
        assert result == 135370

    def test_string_path(self):
        result = xcf_file_size_mod_103_times_1800_plus_image_type_times_2100_plus_width_times_200_plus_height_times_170(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_103_times_1800_plus_image_type_times_2100_plus_width_times_200_plus_height_times_170(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes23PlusImageTypeTimes2400PlusWidthTimesHeightTimes800:
    def test_returns_int(self):
        result = xcf_file_size_times_23_plus_image_type_times_2400_plus_width_times_height_times_800(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_23_plus_image_type_times_2400_plus_width_times_height_times_800(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_23_plus_image_type_times_2400_plus_width_times_height_times_800(_XCF)
        assert result == 4894

    def test_string_path(self):
        result = xcf_file_size_times_23_plus_image_type_times_2400_plus_width_times_height_times_800(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_23_plus_image_type_times_2400_plus_width_times_height_times_800(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
