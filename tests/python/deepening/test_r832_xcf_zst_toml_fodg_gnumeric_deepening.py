"""Sprint R832 — XCF compound analytics deepening tests (Sprint 279)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_71_times_1200_plus_image_type_times_1500_plus_width_times_140_plus_height_times_110,
    xcf_file_size_times_17_plus_image_type_times_1800_plus_width_times_height_times_500,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod71Times1200PlusImageTypeTimes1500PlusWidthTimes140PlusHeightTimes110:
    def test_returns_int(self):
        result = xcf_file_size_mod_71_times_1200_plus_image_type_times_1500_plus_width_times_140_plus_height_times_110(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_71_times_1200_plus_image_type_times_1500_plus_width_times_140_plus_height_times_110(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_71_times_1200_plus_image_type_times_1500_plus_width_times_140_plus_height_times_110(_XCF)
        assert result == 43450

    def test_string_path(self):
        result = xcf_file_size_mod_71_times_1200_plus_image_type_times_1500_plus_width_times_140_plus_height_times_110(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_71_times_1200_plus_image_type_times_1500_plus_width_times_140_plus_height_times_110(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes17PlusImageTypeTimes1800PlusWidthTimesHeightTimes500:
    def test_returns_int(self):
        result = xcf_file_size_times_17_plus_image_type_times_1800_plus_width_times_height_times_500(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_17_plus_image_type_times_1800_plus_width_times_height_times_500(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_17_plus_image_type_times_1800_plus_width_times_height_times_500(_XCF)
        assert result == 3526

    def test_string_path(self):
        result = xcf_file_size_times_17_plus_image_type_times_1800_plus_width_times_height_times_500(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_17_plus_image_type_times_1800_plus_width_times_height_times_500(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
