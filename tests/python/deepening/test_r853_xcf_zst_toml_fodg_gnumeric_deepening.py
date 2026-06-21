"""Sprint R853 — XCF compound analytics deepening tests (Sprint 300)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_113_times_1900_plus_image_type_times_2200_plus_width_times_210_plus_height_times_180,
    xcf_file_size_times_25_plus_image_type_times_2500_plus_width_times_height_times_850,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod113Times1900PlusImageTypeTimes2200PlusWidthTimes210PlusHeightTimes180:
    def test_returns_int(self):
        result = xcf_file_size_mod_113_times_1900_plus_image_type_times_2200_plus_width_times_210_plus_height_times_180(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_113_times_1900_plus_image_type_times_2200_plus_width_times_210_plus_height_times_180(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_113_times_1900_plus_image_type_times_2200_plus_width_times_210_plus_height_times_180(_XCF)
        assert result == 123890

    def test_string_path(self):
        result = xcf_file_size_mod_113_times_1900_plus_image_type_times_2200_plus_width_times_210_plus_height_times_180(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_113_times_1900_plus_image_type_times_2200_plus_width_times_210_plus_height_times_180(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes25PlusImageTypeTimes2500PlusWidthTimesHeightTimes850:
    def test_returns_int(self):
        result = xcf_file_size_times_25_plus_image_type_times_2500_plus_width_times_height_times_850(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_25_plus_image_type_times_2500_plus_width_times_height_times_850(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_25_plus_image_type_times_2500_plus_width_times_height_times_850(_XCF)
        assert result == 5300

    def test_string_path(self):
        result = xcf_file_size_times_25_plus_image_type_times_2500_plus_width_times_height_times_850(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_25_plus_image_type_times_2500_plus_width_times_height_times_850(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
