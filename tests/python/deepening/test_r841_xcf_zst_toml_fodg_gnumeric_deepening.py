"""Sprint R841 — XCF compound analytics deepening tests (Sprint 288)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_89_times_1500_plus_image_type_times_1800_plus_width_times_170_plus_height_times_140,
    xcf_file_size_times_20_plus_image_type_times_2100_plus_width_times_height_times_650,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod89Times1500PlusImageTypeTimes1800PlusWidthTimes170PlusHeightTimes140:
    def test_returns_int(self):
        result = xcf_file_size_mod_89_times_1500_plus_image_type_times_1800_plus_width_times_170_plus_height_times_140(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_89_times_1500_plus_image_type_times_1800_plus_width_times_170_plus_height_times_140(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_89_times_1500_plus_image_type_times_1800_plus_width_times_170_plus_height_times_140(_XCF)
        assert result == 310

    def test_string_path(self):
        result = xcf_file_size_mod_89_times_1500_plus_image_type_times_1800_plus_width_times_170_plus_height_times_140(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_89_times_1500_plus_image_type_times_1800_plus_width_times_170_plus_height_times_140(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes20PlusImageTypeTimes2100PlusWidthTimesHeightTimes650:
    def test_returns_int(self):
        result = xcf_file_size_times_20_plus_image_type_times_2100_plus_width_times_height_times_650(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_20_plus_image_type_times_2100_plus_width_times_height_times_650(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_20_plus_image_type_times_2100_plus_width_times_height_times_650(_XCF)
        assert result == 4210

    def test_string_path(self):
        result = xcf_file_size_times_20_plus_image_type_times_2100_plus_width_times_height_times_650(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_20_plus_image_type_times_2100_plus_width_times_height_times_650(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
