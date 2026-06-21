"""Sprint R886 — XCF compound analytics deepening tests (Sprint 333)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_181_times_2500_plus_image_type_times_3300_plus_width_times_330_plus_height_times_300,
    xcf_file_size_times_43_plus_image_type_times_3700_plus_width_times_height_times_1450,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod181Times2500PlusImageTypeTimes3300PlusWidthTimes330PlusHeightTimes300:
    def test_returns_int(self):
        result = xcf_file_size_mod_181_times_2500_plus_image_type_times_3300_plus_width_times_330_plus_height_times_300(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_181_times_2500_plus_image_type_times_3300_plus_width_times_330_plus_height_times_300(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_181_times_2500_plus_image_type_times_3300_plus_width_times_330_plus_height_times_300(_XCF)
        assert result == 445630

    def test_string_path(self):
        result = xcf_file_size_mod_181_times_2500_plus_image_type_times_3300_plus_width_times_330_plus_height_times_300(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_181_times_2500_plus_image_type_times_3300_plus_width_times_330_plus_height_times_300(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes43PlusImageTypeTimes3700PlusWidthTimesHeightTimes1450:
    def test_returns_int(self):
        result = xcf_file_size_times_43_plus_image_type_times_3700_plus_width_times_height_times_1450(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_43_plus_image_type_times_3700_plus_width_times_height_times_1450(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_43_plus_image_type_times_3700_plus_width_times_height_times_1450(_XCF)
        assert result == 9104

    def test_string_path(self):
        result = xcf_file_size_times_43_plus_image_type_times_3700_plus_width_times_height_times_1450(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_43_plus_image_type_times_3700_plus_width_times_height_times_1450(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
