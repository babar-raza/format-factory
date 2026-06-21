"""Sprint R901 — XCF compound analytics deepening tests (Sprint 348)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_211_times_2800_plus_image_type_times_3900_plus_width_times_390_plus_height_times_360,
    xcf_file_size_times_57_plus_image_type_times_4300_plus_width_times_height_times_1750,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod211Times2800PlusImageTypeTimes3900PlusWidthTimes390PlusHeightTimes360:
    def test_returns_int(self):
        result = xcf_file_size_mod_211_times_2800_plus_image_type_times_3900_plus_width_times_390_plus_height_times_360(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_211_times_2800_plus_image_type_times_3900_plus_width_times_390_plus_height_times_360(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_211_times_2800_plus_image_type_times_3900_plus_width_times_390_plus_height_times_360(_XCF)
        assert result == 499150

    def test_string_path(self):
        result = xcf_file_size_mod_211_times_2800_plus_image_type_times_3900_plus_width_times_390_plus_height_times_360(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_211_times_2800_plus_image_type_times_3900_plus_width_times_390_plus_height_times_360(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes57PlusImageTypeTimes4300PlusWidthTimesHeightTimes1750:
    def test_returns_int(self):
        result = xcf_file_size_times_57_plus_image_type_times_4300_plus_width_times_height_times_1750(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_57_plus_image_type_times_4300_plus_width_times_height_times_1750(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_57_plus_image_type_times_4300_plus_width_times_height_times_1750(_XCF)
        assert result == 11896

    def test_string_path(self):
        result = xcf_file_size_times_57_plus_image_type_times_4300_plus_width_times_height_times_1750(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_57_plus_image_type_times_4300_plus_width_times_height_times_1750(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
