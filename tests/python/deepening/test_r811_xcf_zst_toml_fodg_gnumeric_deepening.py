"""Sprint R811 — XCF compound analytics deepening tests (Sprint 258)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_37_times_500_plus_image_type_times_800_plus_width_times_70_plus_height_times_40,
    xcf_file_size_times_10_plus_image_type_times_1100_plus_width_times_height_times_200,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod37Times500PlusImageTypeTimes800PlusWidthTimes70PlusHeightTimes40:
    def test_returns_int(self):
        result = xcf_file_size_mod_37_times_500_plus_image_type_times_800_plus_width_times_70_plus_height_times_40(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_37_times_500_plus_image_type_times_800_plus_width_times_70_plus_height_times_40(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_37_times_500_plus_image_type_times_800_plus_width_times_70_plus_height_times_40(_XCF)
        assert result == 15110

    def test_string_path(self):
        result = xcf_file_size_mod_37_times_500_plus_image_type_times_800_plus_width_times_70_plus_height_times_40(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_37_times_500_plus_image_type_times_800_plus_width_times_70_plus_height_times_40(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes10PlusImageTypeTimes1100PlusWidthTimesHeightTimes200:
    def test_returns_int(self):
        result = xcf_file_size_times_10_plus_image_type_times_1100_plus_width_times_height_times_200(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_10_plus_image_type_times_1100_plus_width_times_height_times_200(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_10_plus_image_type_times_1100_plus_width_times_height_times_200(_XCF)
        assert result == 1980

    def test_string_path(self):
        result = xcf_file_size_times_10_plus_image_type_times_1100_plus_width_times_height_times_200(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_10_plus_image_type_times_1100_plus_width_times_height_times_200(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
