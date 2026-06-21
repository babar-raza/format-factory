"""Sprint R838 — XCF compound analytics deepening tests (Sprint 285)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_83_times_1400_plus_image_type_times_1700_plus_width_times_160_plus_height_times_130,
    xcf_file_size_times_19_plus_image_type_times_2000_plus_width_times_height_times_600,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod83Times1400PlusImageTypeTimes1700PlusWidthTimes160PlusHeightTimes130:
    def test_returns_int(self):
        result = xcf_file_size_mod_83_times_1400_plus_image_type_times_1700_plus_width_times_160_plus_height_times_130(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_83_times_1400_plus_image_type_times_1700_plus_width_times_160_plus_height_times_130(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_83_times_1400_plus_image_type_times_1700_plus_width_times_160_plus_height_times_130(_XCF)
        assert result == 17090

    def test_string_path(self):
        result = xcf_file_size_mod_83_times_1400_plus_image_type_times_1700_plus_width_times_160_plus_height_times_130(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_83_times_1400_plus_image_type_times_1700_plus_width_times_160_plus_height_times_130(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes19PlusImageTypeTimes2000PlusWidthTimesHeightTimes600:
    def test_returns_int(self):
        result = xcf_file_size_times_19_plus_image_type_times_2000_plus_width_times_height_times_600(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_19_plus_image_type_times_2000_plus_width_times_height_times_600(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_19_plus_image_type_times_2000_plus_width_times_height_times_600(_XCF)
        assert result == 3982

    def test_string_path(self):
        result = xcf_file_size_times_19_plus_image_type_times_2000_plus_width_times_height_times_600(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_19_plus_image_type_times_2000_plus_width_times_height_times_600(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
