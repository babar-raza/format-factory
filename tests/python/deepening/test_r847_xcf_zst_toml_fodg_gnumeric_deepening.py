"""Sprint R847 — XCF compound analytics deepening tests (Sprint 294)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_101_times_1700_plus_image_type_times_2000_plus_width_times_190_plus_height_times_160,
    xcf_file_size_times_22_plus_image_type_times_2300_plus_width_times_height_times_750,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod101Times1700PlusImageTypeTimes2000PlusWidthTimes190PlusHeightTimes160:
    def test_returns_int(self):
        result = xcf_file_size_mod_101_times_1700_plus_image_type_times_2000_plus_width_times_190_plus_height_times_160(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_101_times_1700_plus_image_type_times_2000_plus_width_times_190_plus_height_times_160(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_101_times_1700_plus_image_type_times_2000_plus_width_times_190_plus_height_times_160(_XCF)
        assert result == 131250

    def test_string_path(self):
        result = xcf_file_size_mod_101_times_1700_plus_image_type_times_2000_plus_width_times_190_plus_height_times_160(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_101_times_1700_plus_image_type_times_2000_plus_width_times_190_plus_height_times_160(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes22PlusImageTypeTimes2300PlusWidthTimesHeightTimes750:
    def test_returns_int(self):
        result = xcf_file_size_times_22_plus_image_type_times_2300_plus_width_times_height_times_750(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_22_plus_image_type_times_2300_plus_width_times_height_times_750(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_22_plus_image_type_times_2300_plus_width_times_height_times_750(_XCF)
        assert result == 4666

    def test_string_path(self):
        result = xcf_file_size_times_22_plus_image_type_times_2300_plus_width_times_height_times_750(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_22_plus_image_type_times_2300_plus_width_times_height_times_750(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
