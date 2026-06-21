"""Sprint R862 — XCF compound analytics deepening tests (Sprint 309)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_137_times_2050_plus_image_type_times_2500_plus_width_times_240_plus_height_times_210,
    xcf_file_size_times_28_plus_image_type_times_2800_plus_width_times_height_times_1000,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod137Times2050PlusImageTypeTimes2500PlusWidthTimes240PlusHeightTimes210:
    def test_returns_int(self):
        result = xcf_file_size_mod_137_times_2050_plus_image_type_times_2500_plus_width_times_240_plus_height_times_210(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_137_times_2050_plus_image_type_times_2500_plus_width_times_240_plus_height_times_210(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_137_times_2050_plus_image_type_times_2500_plus_width_times_240_plus_height_times_210(_XCF)
        assert result == 84500

    def test_string_path(self):
        result = xcf_file_size_mod_137_times_2050_plus_image_type_times_2500_plus_width_times_240_plus_height_times_210(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_137_times_2050_plus_image_type_times_2500_plus_width_times_240_plus_height_times_210(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes28PlusImageTypeTimes2800PlusWidthTimesHeightTimes1000:
    def test_returns_int(self):
        result = xcf_file_size_times_28_plus_image_type_times_2800_plus_width_times_height_times_1000(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_28_plus_image_type_times_2800_plus_width_times_height_times_1000(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_28_plus_image_type_times_2800_plus_width_times_height_times_1000(_XCF)
        assert result == 5984

    def test_string_path(self):
        result = xcf_file_size_times_28_plus_image_type_times_2800_plus_width_times_height_times_1000(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_28_plus_image_type_times_2800_plus_width_times_height_times_1000(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
