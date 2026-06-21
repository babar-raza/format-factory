"""Sprint R829 — XCF compound analytics deepening tests (Sprint 276)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_67_times_1100_plus_image_type_times_1400_plus_width_times_130_plus_height_times_100,
    xcf_file_size_times_16_plus_image_type_times_1700_plus_width_times_height_times_450,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod67Times1100PlusImageTypeTimes1400PlusWidthTimes130PlusHeightTimes100:
    def test_returns_int(self):
        result = xcf_file_size_mod_67_times_1100_plus_image_type_times_1400_plus_width_times_130_plus_height_times_100(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_67_times_1100_plus_image_type_times_1400_plus_width_times_130_plus_height_times_100(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_67_times_1100_plus_image_type_times_1400_plus_width_times_130_plus_height_times_100(_XCF)
        assert result == 48630

    def test_string_path(self):
        result = xcf_file_size_mod_67_times_1100_plus_image_type_times_1400_plus_width_times_130_plus_height_times_100(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_67_times_1100_plus_image_type_times_1400_plus_width_times_130_plus_height_times_100(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes16PlusImageTypeTimes1700PlusWidthTimesHeightTimes450:
    def test_returns_int(self):
        result = xcf_file_size_times_16_plus_image_type_times_1700_plus_width_times_height_times_450(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_16_plus_image_type_times_1700_plus_width_times_height_times_450(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_16_plus_image_type_times_1700_plus_width_times_height_times_450(_XCF)
        assert result == 3298

    def test_string_path(self):
        result = xcf_file_size_times_16_plus_image_type_times_1700_plus_width_times_height_times_450(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_16_plus_image_type_times_1700_plus_width_times_height_times_450(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
