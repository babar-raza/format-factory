"""Sprint R865 — XCF compound analytics deepening tests (Sprint 312)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_139_times_2100_plus_image_type_times_2600_plus_width_times_250_plus_height_times_220,
    xcf_file_size_times_29_plus_image_type_times_2900_plus_width_times_height_times_1050,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod139Times2100PlusImageTypeTimes2600PlusWidthTimes250PlusHeightTimes220:
    def test_returns_int(self):
        result = xcf_file_size_mod_139_times_2100_plus_image_type_times_2600_plus_width_times_250_plus_height_times_220(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_139_times_2100_plus_image_type_times_2600_plus_width_times_250_plus_height_times_220(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_139_times_2100_plus_image_type_times_2600_plus_width_times_250_plus_height_times_220(_XCF)
        assert result == 82370

    def test_string_path(self):
        result = xcf_file_size_mod_139_times_2100_plus_image_type_times_2600_plus_width_times_250_plus_height_times_220(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_139_times_2100_plus_image_type_times_2600_plus_width_times_250_plus_height_times_220(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes29PlusImageTypeTimes2900PlusWidthTimesHeightTimes1050:
    def test_returns_int(self):
        result = xcf_file_size_times_29_plus_image_type_times_2900_plus_width_times_height_times_1050(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_29_plus_image_type_times_2900_plus_width_times_height_times_1050(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_29_plus_image_type_times_2900_plus_width_times_height_times_1050(_XCF)
        assert result == 6212

    def test_string_path(self):
        result = xcf_file_size_times_29_plus_image_type_times_2900_plus_width_times_height_times_1050(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_29_plus_image_type_times_2900_plus_width_times_height_times_1050(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
