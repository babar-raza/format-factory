"""Sprint R868 — XCF compound analytics deepening tests (Sprint 315)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_149_times_2150_plus_image_type_times_2700_plus_width_times_260_plus_height_times_230,
    xcf_file_size_times_30_plus_image_type_times_3000_plus_width_times_height_times_1100,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod149Times2150PlusImageTypeTimes2700PlusWidthTimes260PlusHeightTimes230:
    def test_returns_int(self):
        result = xcf_file_size_mod_149_times_2150_plus_image_type_times_2700_plus_width_times_260_plus_height_times_230(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_149_times_2150_plus_image_type_times_2700_plus_width_times_260_plus_height_times_230(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_149_times_2150_plus_image_type_times_2700_plus_width_times_260_plus_height_times_230(_XCF)
        assert result == 62840

    def test_string_path(self):
        result = xcf_file_size_mod_149_times_2150_plus_image_type_times_2700_plus_width_times_260_plus_height_times_230(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_149_times_2150_plus_image_type_times_2700_plus_width_times_260_plus_height_times_230(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes30PlusImageTypeTimes3000PlusWidthTimesHeightTimes1100:
    def test_returns_int(self):
        result = xcf_file_size_times_30_plus_image_type_times_3000_plus_width_times_height_times_1100(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_30_plus_image_type_times_3000_plus_width_times_height_times_1100(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_30_plus_image_type_times_3000_plus_width_times_height_times_1100(_XCF)
        assert result == 6440

    def test_string_path(self):
        result = xcf_file_size_times_30_plus_image_type_times_3000_plus_width_times_height_times_1100(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_30_plus_image_type_times_3000_plus_width_times_height_times_1100(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
