"""Sprint R859 — XCF compound analytics deepening tests (Sprint 306)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_131_times_2000_plus_image_type_times_2400_plus_width_times_230_plus_height_times_200,
    xcf_file_size_times_27_plus_image_type_times_2700_plus_width_times_height_times_950,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod131Times2000PlusImageTypeTimes2400PlusWidthTimes230PlusHeightTimes200:
    def test_returns_int(self):
        result = xcf_file_size_mod_131_times_2000_plus_image_type_times_2400_plus_width_times_230_plus_height_times_200(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_131_times_2000_plus_image_type_times_2400_plus_width_times_230_plus_height_times_200(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_131_times_2000_plus_image_type_times_2400_plus_width_times_230_plus_height_times_200(_XCF)
        assert result == 94430

    def test_string_path(self):
        result = xcf_file_size_mod_131_times_2000_plus_image_type_times_2400_plus_width_times_230_plus_height_times_200(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_131_times_2000_plus_image_type_times_2400_plus_width_times_230_plus_height_times_200(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes27PlusImageTypeTimes2700PlusWidthTimesHeightTimes950:
    def test_returns_int(self):
        result = xcf_file_size_times_27_plus_image_type_times_2700_plus_width_times_height_times_950(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_27_plus_image_type_times_2700_plus_width_times_height_times_950(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_27_plus_image_type_times_2700_plus_width_times_height_times_950(_XCF)
        assert result == 5756

    def test_string_path(self):
        result = xcf_file_size_times_27_plus_image_type_times_2700_plus_width_times_height_times_950(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_27_plus_image_type_times_2700_plus_width_times_height_times_950(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
