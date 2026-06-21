"""Sprint R892 — XCF compound analytics deepening tests (Sprint 339)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_197_times_2650_plus_image_type_times_3600_plus_width_times_360_plus_height_times_330,
    xcf_file_size_times_49_plus_image_type_times_4000_plus_width_times_height_times_1600,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod197Times2650PlusImageTypeTimes3600PlusWidthTimes360PlusHeightTimes330:
    def test_returns_int(self):
        result = xcf_file_size_mod_197_times_2650_plus_image_type_times_3600_plus_width_times_360_plus_height_times_330(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_197_times_2650_plus_image_type_times_3600_plus_width_times_360_plus_height_times_330(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_197_times_2650_plus_image_type_times_3600_plus_width_times_360_plus_height_times_330(_XCF)
        assert result == 472390

    def test_string_path(self):
        result = xcf_file_size_mod_197_times_2650_plus_image_type_times_3600_plus_width_times_360_plus_height_times_330(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_197_times_2650_plus_image_type_times_3600_plus_width_times_360_plus_height_times_330(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes49PlusImageTypeTimes4000PlusWidthTimesHeightTimes1600:
    def test_returns_int(self):
        result = xcf_file_size_times_49_plus_image_type_times_4000_plus_width_times_height_times_1600(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_49_plus_image_type_times_4000_plus_width_times_height_times_1600(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_49_plus_image_type_times_4000_plus_width_times_height_times_1600(_XCF)
        assert result == 10322

    def test_string_path(self):
        result = xcf_file_size_times_49_plus_image_type_times_4000_plus_width_times_height_times_1600(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_49_plus_image_type_times_4000_plus_width_times_height_times_1600(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
