"""Sprint R874 — XCF compound analytics deepening tests (Sprint 321)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_157_times_2250_plus_image_type_times_2900_plus_width_times_280_plus_height_times_250,
    xcf_file_size_times_33_plus_image_type_times_3200_plus_width_times_height_times_1200,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod157Times2250PlusImageTypeTimes2900PlusWidthTimes280PlusHeightTimes250:
    def test_returns_int(self):
        result = xcf_file_size_mod_157_times_2250_plus_image_type_times_2900_plus_width_times_280_plus_height_times_250(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_157_times_2250_plus_image_type_times_2900_plus_width_times_280_plus_height_times_250(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_157_times_2250_plus_image_type_times_2900_plus_width_times_280_plus_height_times_250(_XCF)
        assert result == 47780

    def test_string_path(self):
        result = xcf_file_size_mod_157_times_2250_plus_image_type_times_2900_plus_width_times_280_plus_height_times_250(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_157_times_2250_plus_image_type_times_2900_plus_width_times_280_plus_height_times_250(
            SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf"
        )
        assert isinstance(result, int)


class TestXcfFileSizeTimes33PlusImageTypeTimes3200PlusWidthTimesHeightTimes1200:
    def test_returns_int(self):
        result = xcf_file_size_times_33_plus_image_type_times_3200_plus_width_times_height_times_1200(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_33_plus_image_type_times_3200_plus_width_times_height_times_1200(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_33_plus_image_type_times_3200_plus_width_times_height_times_1200(_XCF)
        assert result == 7074

    def test_string_path(self):
        result = xcf_file_size_times_33_plus_image_type_times_3200_plus_width_times_height_times_1200(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_33_plus_image_type_times_3200_plus_width_times_height_times_1200(
            SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf"
        )
        assert isinstance(result, int)
