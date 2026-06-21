"""Sprint R844 — XCF compound analytics deepening tests (Sprint 291)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_97_times_1600_plus_image_type_times_1900_plus_width_times_180_plus_height_times_150,
    xcf_file_size_times_21_plus_image_type_times_2200_plus_width_times_height_times_700,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod97Times1600PlusImageTypeTimes1900PlusWidthTimes180PlusHeightTimes150:
    def test_returns_int(self):
        result = xcf_file_size_mod_97_times_1600_plus_image_type_times_1900_plus_width_times_180_plus_height_times_150(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_97_times_1600_plus_image_type_times_1900_plus_width_times_180_plus_height_times_150(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_97_times_1600_plus_image_type_times_1900_plus_width_times_180_plus_height_times_150(_XCF)
        assert result == 129930

    def test_string_path(self):
        result = xcf_file_size_mod_97_times_1600_plus_image_type_times_1900_plus_width_times_180_plus_height_times_150(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_97_times_1600_plus_image_type_times_1900_plus_width_times_180_plus_height_times_150(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes21PlusImageTypeTimes2200PlusWidthTimesHeightTimes700:
    def test_returns_int(self):
        result = xcf_file_size_times_21_plus_image_type_times_2200_plus_width_times_height_times_700(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_21_plus_image_type_times_2200_plus_width_times_height_times_700(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_21_plus_image_type_times_2200_plus_width_times_height_times_700(_XCF)
        assert result == 4438

    def test_string_path(self):
        result = xcf_file_size_times_21_plus_image_type_times_2200_plus_width_times_height_times_700(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_21_plus_image_type_times_2200_plus_width_times_height_times_700(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
