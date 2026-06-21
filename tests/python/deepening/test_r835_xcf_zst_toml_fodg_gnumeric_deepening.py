"""Sprint R835 — XCF compound analytics deepening tests (Sprint 282)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_79_times_1300_plus_image_type_times_1600_plus_width_times_150_plus_height_times_120,
    xcf_file_size_times_18_plus_image_type_times_1900_plus_width_times_height_times_550,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod79Times1300PlusImageTypeTimes1600PlusWidthTimes150PlusHeightTimes120:
    def test_returns_int(self):
        result = xcf_file_size_mod_79_times_1300_plus_image_type_times_1600_plus_width_times_150_plus_height_times_120(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_79_times_1300_plus_image_type_times_1600_plus_width_times_150_plus_height_times_120(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_79_times_1300_plus_image_type_times_1600_plus_width_times_150_plus_height_times_120(_XCF)
        assert result == 26270

    def test_string_path(self):
        result = xcf_file_size_mod_79_times_1300_plus_image_type_times_1600_plus_width_times_150_plus_height_times_120(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_79_times_1300_plus_image_type_times_1600_plus_width_times_150_plus_height_times_120(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes18PlusImageTypeTimes1900PlusWidthTimesHeightTimes550:
    def test_returns_int(self):
        result = xcf_file_size_times_18_plus_image_type_times_1900_plus_width_times_height_times_550(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_18_plus_image_type_times_1900_plus_width_times_height_times_550(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_18_plus_image_type_times_1900_plus_width_times_height_times_550(_XCF)
        assert result == 3754

    def test_string_path(self):
        result = xcf_file_size_times_18_plus_image_type_times_1900_plus_width_times_height_times_550(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_18_plus_image_type_times_1900_plus_width_times_height_times_550(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
