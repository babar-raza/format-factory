"""Sprint R823 — XCF compound analytics deepening tests (Sprint 270)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_59_times_900_plus_image_type_times_1200_plus_width_times_110_plus_height_times_80,
    xcf_file_size_times_14_plus_image_type_times_1500_plus_width_times_height_times_350,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod59Times900PlusImageTypeTimes1200PlusWidthTimes110PlusHeightTimes80:
    def test_returns_int(self):
        result = xcf_file_size_mod_59_times_900_plus_image_type_times_1200_plus_width_times_110_plus_height_times_80(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_59_times_900_plus_image_type_times_1200_plus_width_times_110_plus_height_times_80(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_59_times_900_plus_image_type_times_1200_plus_width_times_110_plus_height_times_80(_XCF)
        assert result == 1090

    def test_string_path(self):
        result = xcf_file_size_mod_59_times_900_plus_image_type_times_1200_plus_width_times_110_plus_height_times_80(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_59_times_900_plus_image_type_times_1200_plus_width_times_110_plus_height_times_80(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes14PlusImageTypeTimes1500PlusWidthTimesHeightTimes350:
    def test_returns_int(self):
        result = xcf_file_size_times_14_plus_image_type_times_1500_plus_width_times_height_times_350(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_14_plus_image_type_times_1500_plus_width_times_height_times_350(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_14_plus_image_type_times_1500_plus_width_times_height_times_350(_XCF)
        assert result == 2842

    def test_string_path(self):
        result = xcf_file_size_times_14_plus_image_type_times_1500_plus_width_times_height_times_350(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_14_plus_image_type_times_1500_plus_width_times_height_times_350(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
