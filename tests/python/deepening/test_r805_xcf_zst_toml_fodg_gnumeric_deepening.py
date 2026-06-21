"""Sprint R805 — XCF compound analytics deepening tests (Sprint 252)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_23_times_300_plus_image_type_times_600_plus_width_times_40_plus_height_times_20,
    xcf_file_size_times_7_plus_image_type_times_900_plus_width_times_height_times_150,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod23Times300PlusImageTypeTimes600PlusWidthTimes40PlusHeightTimes20:
    def test_returns_int(self):
        result = xcf_file_size_mod_23_times_300_plus_image_type_times_600_plus_width_times_40_plus_height_times_20(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_23_times_300_plus_image_type_times_600_plus_width_times_40_plus_height_times_20(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_23_times_300_plus_image_type_times_600_plus_width_times_40_plus_height_times_20(_XCF)
        assert result == 5160

    def test_string_path(self):
        result = xcf_file_size_mod_23_times_300_plus_image_type_times_600_plus_width_times_40_plus_height_times_20(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_23_times_300_plus_image_type_times_600_plus_width_times_40_plus_height_times_20(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes7PlusImageTypeTimes900PlusWidthTimesHeightTimes150:
    def test_returns_int(self):
        result = xcf_file_size_times_7_plus_image_type_times_900_plus_width_times_height_times_150(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_7_plus_image_type_times_900_plus_width_times_height_times_150(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_7_plus_image_type_times_900_plus_width_times_height_times_150(_XCF)
        assert result == 1396

    def test_string_path(self):
        result = xcf_file_size_times_7_plus_image_type_times_900_plus_width_times_height_times_150(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_7_plus_image_type_times_900_plus_width_times_height_times_150(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
