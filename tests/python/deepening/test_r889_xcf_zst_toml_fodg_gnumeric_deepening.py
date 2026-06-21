"""Sprint R889 — XCF compound analytics deepening tests (Sprint 336)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_193_times_2600_plus_image_type_times_3500_plus_width_times_350_plus_height_times_320,
    xcf_file_size_times_47_plus_image_type_times_3900_plus_width_times_height_times_1550,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod193Times2600PlusImageTypeTimes3500PlusWidthTimes350PlusHeightTimes320:
    def test_returns_int(self):
        result = xcf_file_size_mod_193_times_2600_plus_image_type_times_3500_plus_width_times_350_plus_height_times_320(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_193_times_2600_plus_image_type_times_3500_plus_width_times_350_plus_height_times_320(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_193_times_2600_plus_image_type_times_3500_plus_width_times_350_plus_height_times_320(_XCF)
        assert result == 463470

    def test_string_path(self):
        result = xcf_file_size_mod_193_times_2600_plus_image_type_times_3500_plus_width_times_350_plus_height_times_320(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_193_times_2600_plus_image_type_times_3500_plus_width_times_350_plus_height_times_320(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes47PlusImageTypeTimes3900PlusWidthTimesHeightTimes1550:
    def test_returns_int(self):
        result = xcf_file_size_times_47_plus_image_type_times_3900_plus_width_times_height_times_1550(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_47_plus_image_type_times_3900_plus_width_times_height_times_1550(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_47_plus_image_type_times_3900_plus_width_times_height_times_1550(_XCF)
        assert result == 9916

    def test_string_path(self):
        result = xcf_file_size_times_47_plus_image_type_times_3900_plus_width_times_height_times_1550(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_47_plus_image_type_times_3900_plus_width_times_height_times_1550(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
