"""Sprint R871 — XCF compound analytics deepening tests (Sprint 318)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_151_times_2200_plus_image_type_times_2800_plus_width_times_270_plus_height_times_240,
    xcf_file_size_times_31_plus_image_type_times_3100_plus_width_times_height_times_1150,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod151Times2200PlusImageTypeTimes2800PlusWidthTimes270PlusHeightTimes240:
    def test_returns_int(self):
        result = xcf_file_size_mod_151_times_2200_plus_image_type_times_2800_plus_width_times_270_plus_height_times_240(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_151_times_2200_plus_image_type_times_2800_plus_width_times_270_plus_height_times_240(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_151_times_2200_plus_image_type_times_2800_plus_width_times_270_plus_height_times_240(_XCF)
        assert result == 59910

    def test_string_path(self):
        result = xcf_file_size_mod_151_times_2200_plus_image_type_times_2800_plus_width_times_270_plus_height_times_240(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_151_times_2200_plus_image_type_times_2800_plus_width_times_270_plus_height_times_240(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes31PlusImageTypeTimes3100PlusWidthTimesHeightTimes1150:
    def test_returns_int(self):
        result = xcf_file_size_times_31_plus_image_type_times_3100_plus_width_times_height_times_1150(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_31_plus_image_type_times_3100_plus_width_times_height_times_1150(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_31_plus_image_type_times_3100_plus_width_times_height_times_1150(_XCF)
        assert result == 6668

    def test_string_path(self):
        result = xcf_file_size_times_31_plus_image_type_times_3100_plus_width_times_height_times_1150(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_31_plus_image_type_times_3100_plus_width_times_height_times_1150(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
