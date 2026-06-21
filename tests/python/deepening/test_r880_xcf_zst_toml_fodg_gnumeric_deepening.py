"""Sprint R880 — XCF compound analytics deepening tests (Sprint 327)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_167_times_2350_plus_image_type_times_3100_plus_width_times_300_plus_height_times_270,
    xcf_file_size_times_37_plus_image_type_times_3400_plus_width_times_height_times_1300,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod167Times2350PlusImageTypeTimes3100PlusWidthTimes300PlusHeightTimes270:
    def test_returns_int(self):
        result = xcf_file_size_mod_167_times_2350_plus_image_type_times_3100_plus_width_times_300_plus_height_times_270(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_167_times_2350_plus_image_type_times_3100_plus_width_times_300_plus_height_times_270(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_167_times_2350_plus_image_type_times_3100_plus_width_times_300_plus_height_times_270(_XCF)
        assert result == 26420

    def test_string_path(self):
        result = xcf_file_size_mod_167_times_2350_plus_image_type_times_3100_plus_width_times_300_plus_height_times_270(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_167_times_2350_plus_image_type_times_3100_plus_width_times_300_plus_height_times_270(
            SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf"
        )
        assert isinstance(result, int)


class TestXcfFileSizeTimes37PlusImageTypeTimes3400PlusWidthTimesHeightTimes1300:
    def test_returns_int(self):
        result = xcf_file_size_times_37_plus_image_type_times_3400_plus_width_times_height_times_1300(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_37_plus_image_type_times_3400_plus_width_times_height_times_1300(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_37_plus_image_type_times_3400_plus_width_times_height_times_1300(_XCF)
        assert result == 7886

    def test_string_path(self):
        result = xcf_file_size_times_37_plus_image_type_times_3400_plus_width_times_height_times_1300(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_37_plus_image_type_times_3400_plus_width_times_height_times_1300(
            SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf"
        )
        assert isinstance(result, int)
