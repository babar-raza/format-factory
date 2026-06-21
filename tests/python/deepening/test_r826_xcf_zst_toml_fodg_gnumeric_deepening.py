"""Sprint R826 — XCF compound analytics deepening tests (Sprint 273)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_61_times_1000_plus_image_type_times_1300_plus_width_times_120_plus_height_times_90,
    xcf_file_size_times_15_plus_image_type_times_1600_plus_width_times_height_times_400,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod61Times1000PlusImageTypeTimes1300PlusWidthTimes120PlusHeightTimes90:
    def test_returns_int(self):
        result = xcf_file_size_mod_61_times_1000_plus_image_type_times_1300_plus_width_times_120_plus_height_times_90(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_61_times_1000_plus_image_type_times_1300_plus_width_times_120_plus_height_times_90(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_61_times_1000_plus_image_type_times_1300_plus_width_times_120_plus_height_times_90(_XCF)
        assert result == 56210

    def test_string_path(self):
        result = xcf_file_size_mod_61_times_1000_plus_image_type_times_1300_plus_width_times_120_plus_height_times_90(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_61_times_1000_plus_image_type_times_1300_plus_width_times_120_plus_height_times_90(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes15PlusImageTypeTimes1600PlusWidthTimesHeightTimes400:
    def test_returns_int(self):
        result = xcf_file_size_times_15_plus_image_type_times_1600_plus_width_times_height_times_400(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_15_plus_image_type_times_1600_plus_width_times_height_times_400(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_15_plus_image_type_times_1600_plus_width_times_height_times_400(_XCF)
        assert result == 3070

    def test_string_path(self):
        result = xcf_file_size_times_15_plus_image_type_times_1600_plus_width_times_height_times_400(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_15_plus_image_type_times_1600_plus_width_times_height_times_400(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
