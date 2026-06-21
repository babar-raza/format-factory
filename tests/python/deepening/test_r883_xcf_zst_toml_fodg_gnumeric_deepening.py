"""Sprint R883 — XCF compound analytics deepening tests (Sprint 330)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_173_times_2400_plus_image_type_times_3200_plus_width_times_310_plus_height_times_280,
    xcf_file_size_times_39_plus_image_type_times_3500_plus_width_times_height_times_1350,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod173Times2400PlusImageTypeTimes3200PlusWidthTimes310PlusHeightTimes280:
    def test_returns_int(self):
        result = xcf_file_size_mod_173_times_2400_plus_image_type_times_3200_plus_width_times_310_plus_height_times_280(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_173_times_2400_plus_image_type_times_3200_plus_width_times_310_plus_height_times_280(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_173_times_2400_plus_image_type_times_3200_plus_width_times_310_plus_height_times_280(_XCF)
        assert result == 12590

    def test_string_path(self):
        result = xcf_file_size_mod_173_times_2400_plus_image_type_times_3200_plus_width_times_310_plus_height_times_280(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_173_times_2400_plus_image_type_times_3200_plus_width_times_310_plus_height_times_280(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes39PlusImageTypeTimes3500PlusWidthTimesHeightTimes1350:
    def test_returns_int(self):
        result = xcf_file_size_times_39_plus_image_type_times_3500_plus_width_times_height_times_1350(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_39_plus_image_type_times_3500_plus_width_times_height_times_1350(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_39_plus_image_type_times_3500_plus_width_times_height_times_1350(_XCF)
        assert result == 8292

    def test_string_path(self):
        result = xcf_file_size_times_39_plus_image_type_times_3500_plus_width_times_height_times_1350(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_39_plus_image_type_times_3500_plus_width_times_height_times_1350(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
