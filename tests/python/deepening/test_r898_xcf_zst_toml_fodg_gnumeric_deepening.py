"""Sprint R898 — XCF compound analytics deepening tests (Sprint 345)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_211_times_2750_plus_image_type_times_3800_plus_width_times_380_plus_height_times_350,
    xcf_file_size_times_53_plus_image_type_times_4200_plus_width_times_height_times_1700,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod211Times2750PlusImageTypeTimes3800PlusWidthTimes380PlusHeightTimes350:
    def test_returns_int(self):
        result = xcf_file_size_mod_211_times_2750_plus_image_type_times_3800_plus_width_times_380_plus_height_times_350(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_211_times_2750_plus_image_type_times_3800_plus_width_times_380_plus_height_times_350(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_211_times_2750_plus_image_type_times_3800_plus_width_times_380_plus_height_times_350(_XCF)
        assert result == 490230

    def test_string_path(self):
        result = xcf_file_size_mod_211_times_2750_plus_image_type_times_3800_plus_width_times_380_plus_height_times_350(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_211_times_2750_plus_image_type_times_3800_plus_width_times_380_plus_height_times_350(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes53PlusImageTypeTimes4200PlusWidthTimesHeightTimes1700:
    def test_returns_int(self):
        result = xcf_file_size_times_53_plus_image_type_times_4200_plus_width_times_height_times_1700(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_53_plus_image_type_times_4200_plus_width_times_height_times_1700(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_53_plus_image_type_times_4200_plus_width_times_height_times_1700(_XCF)
        assert result == 11134

    def test_string_path(self):
        result = xcf_file_size_times_53_plus_image_type_times_4200_plus_width_times_height_times_1700(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_53_plus_image_type_times_4200_plus_width_times_height_times_1700(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
