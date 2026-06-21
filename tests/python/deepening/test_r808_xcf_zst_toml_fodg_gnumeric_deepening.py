"""Sprint R808 — XCF compound analytics deepening tests (Sprint 255)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_31_times_400_plus_image_type_times_700_plus_width_times_60_plus_height_times_30,
    xcf_file_size_times_9_plus_image_type_times_1000_plus_width_plus_height_times_80,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod31Times400PlusImageTypeTimes700PlusWidthTimes60PlusHeightTimes30:
    def test_returns_int(self):
        result = xcf_file_size_mod_31_times_400_plus_image_type_times_700_plus_width_times_60_plus_height_times_30(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_31_times_400_plus_image_type_times_700_plus_width_times_60_plus_height_times_30(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_31_times_400_plus_image_type_times_700_plus_width_times_60_plus_height_times_30(_XCF)
        assert result == 9290

    def test_string_path(self):
        result = xcf_file_size_mod_31_times_400_plus_image_type_times_700_plus_width_times_60_plus_height_times_30(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_31_times_400_plus_image_type_times_700_plus_width_times_60_plus_height_times_30(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes9PlusImageTypeTimes1000PlusWidthPlusHeightTimes80:
    def test_returns_int(self):
        result = xcf_file_size_times_9_plus_image_type_times_1000_plus_width_plus_height_times_80(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_9_plus_image_type_times_1000_plus_width_plus_height_times_80(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_9_plus_image_type_times_1000_plus_width_plus_height_times_80(_XCF)
        assert result == 1762

    def test_string_path(self):
        result = xcf_file_size_times_9_plus_image_type_times_1000_plus_width_plus_height_times_80(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_9_plus_image_type_times_1000_plus_width_plus_height_times_80(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
