"""Sprint R814 — XCF compound analytics deepening tests (Sprint 261)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_43_times_600_plus_image_type_times_900_plus_width_times_80_plus_height_times_50,
    xcf_file_size_times_11_plus_image_type_times_1200_plus_width_plus_height_times_90,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod43Times600PlusImageTypeTimes900PlusWidthTimes80PlusHeightTimes50:
    def test_returns_int(self):
        result = xcf_file_size_mod_43_times_600_plus_image_type_times_900_plus_width_times_80_plus_height_times_50(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_43_times_600_plus_image_type_times_900_plus_width_times_80_plus_height_times_50(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_43_times_600_plus_image_type_times_900_plus_width_times_80_plus_height_times_50(_XCF)
        assert result == 3730

    def test_string_path(self):
        result = xcf_file_size_mod_43_times_600_plus_image_type_times_900_plus_width_times_80_plus_height_times_50(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_43_times_600_plus_image_type_times_900_plus_width_times_80_plus_height_times_50(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes11PlusImageTypeTimes1200PlusWidthPlusHeightTimes90:
    def test_returns_int(self):
        result = xcf_file_size_times_11_plus_image_type_times_1200_plus_width_plus_height_times_90(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_11_plus_image_type_times_1200_plus_width_plus_height_times_90(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_11_plus_image_type_times_1200_plus_width_plus_height_times_90(_XCF)
        assert result == 2138

    def test_string_path(self):
        result = xcf_file_size_times_11_plus_image_type_times_1200_plus_width_plus_height_times_90(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_11_plus_image_type_times_1200_plus_width_plus_height_times_90(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
