"""Sprint R817 — XCF compound analytics deepening tests (Sprint 264)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_47_times_700_plus_image_type_times_1000_plus_width_times_90_plus_height_times_60,
    xcf_file_size_times_12_plus_image_type_times_1300_plus_width_times_height_times_250,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod47Times700PlusImageTypeTimes1000PlusWidthTimes90PlusHeightTimes60:
    def test_returns_int(self):
        result = xcf_file_size_mod_47_times_700_plus_image_type_times_1000_plus_width_times_90_plus_height_times_60(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_47_times_700_plus_image_type_times_1000_plus_width_times_90_plus_height_times_60(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_47_times_700_plus_image_type_times_1000_plus_width_times_90_plus_height_times_60(_XCF)
        assert result == 26050

    def test_string_path(self):
        result = xcf_file_size_mod_47_times_700_plus_image_type_times_1000_plus_width_times_90_plus_height_times_60(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_47_times_700_plus_image_type_times_1000_plus_width_times_90_plus_height_times_60(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes12PlusImageTypeTimes1300PlusWidthTimesHeightTimes250:
    def test_returns_int(self):
        result = xcf_file_size_times_12_plus_image_type_times_1300_plus_width_times_height_times_250(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_12_plus_image_type_times_1300_plus_width_times_height_times_250(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_12_plus_image_type_times_1300_plus_width_times_height_times_250(_XCF)
        assert result == 2386

    def test_string_path(self):
        result = xcf_file_size_times_12_plus_image_type_times_1300_plus_width_times_height_times_250(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_12_plus_image_type_times_1300_plus_width_times_height_times_250(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
