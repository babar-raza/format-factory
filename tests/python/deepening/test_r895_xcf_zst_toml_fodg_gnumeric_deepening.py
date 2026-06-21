"""Sprint R895 — XCF compound analytics deepening tests (Sprint 342)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_199_times_2700_plus_image_type_times_3700_plus_width_times_370_plus_height_times_340,
    xcf_file_size_times_51_plus_image_type_times_4100_plus_width_times_height_times_1650,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod199Times2700PlusImageTypeTimes3700PlusWidthTimes370PlusHeightTimes340:
    def test_returns_int(self):
        result = xcf_file_size_mod_199_times_2700_plus_image_type_times_3700_plus_width_times_370_plus_height_times_340(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_199_times_2700_plus_image_type_times_3700_plus_width_times_370_plus_height_times_340(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_199_times_2700_plus_image_type_times_3700_plus_width_times_370_plus_height_times_340(_XCF)
        assert result == 481310

    def test_string_path(self):
        result = xcf_file_size_mod_199_times_2700_plus_image_type_times_3700_plus_width_times_370_plus_height_times_340(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_199_times_2700_plus_image_type_times_3700_plus_width_times_370_plus_height_times_340(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes51PlusImageTypeTimes4100PlusWidthTimesHeightTimes1650:
    def test_returns_int(self):
        result = xcf_file_size_times_51_plus_image_type_times_4100_plus_width_times_height_times_1650(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_51_plus_image_type_times_4100_plus_width_times_height_times_1650(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_51_plus_image_type_times_4100_plus_width_times_height_times_1650(_XCF)
        assert result == 10728

    def test_string_path(self):
        result = xcf_file_size_times_51_plus_image_type_times_4100_plus_width_times_height_times_1650(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_51_plus_image_type_times_4100_plus_width_times_height_times_1650(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
