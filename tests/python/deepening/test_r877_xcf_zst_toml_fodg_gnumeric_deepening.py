"""Sprint R877 — XCF compound analytics deepening tests (Sprint 324)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_163_times_2300_plus_image_type_times_3000_plus_width_times_290_plus_height_times_260,
    xcf_file_size_times_35_plus_image_type_times_3300_plus_width_times_height_times_1250,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod163Times2300PlusImageTypeTimes3000PlusWidthTimes290PlusHeightTimes260:
    def test_returns_int(self):
        result = xcf_file_size_mod_163_times_2300_plus_image_type_times_3000_plus_width_times_290_plus_height_times_260(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_163_times_2300_plus_image_type_times_3000_plus_width_times_290_plus_height_times_260(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_163_times_2300_plus_image_type_times_3000_plus_width_times_290_plus_height_times_260(_XCF)
        assert result == 35050

    def test_string_path(self):
        result = xcf_file_size_mod_163_times_2300_plus_image_type_times_3000_plus_width_times_290_plus_height_times_260(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_163_times_2300_plus_image_type_times_3000_plus_width_times_290_plus_height_times_260(
            SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf"
        )
        assert isinstance(result, int)


class TestXcfFileSizeTimes35PlusImageTypeTimes3300PlusWidthTimesHeightTimes1250:
    def test_returns_int(self):
        result = xcf_file_size_times_35_plus_image_type_times_3300_plus_width_times_height_times_1250(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_35_plus_image_type_times_3300_plus_width_times_height_times_1250(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_35_plus_image_type_times_3300_plus_width_times_height_times_1250(_XCF)
        assert result == 7480

    def test_string_path(self):
        result = xcf_file_size_times_35_plus_image_type_times_3300_plus_width_times_height_times_1250(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_35_plus_image_type_times_3300_plus_width_times_height_times_1250(
            SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf"
        )
        assert isinstance(result, int)
