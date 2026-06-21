"""Sprint R856 — XCF compound analytics deepening tests (Sprint 303)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.xcf import (
    xcf_file_size_mod_127_times_1950_plus_image_type_times_2300_plus_width_times_220_plus_height_times_190,
    xcf_file_size_times_26_plus_image_type_times_2600_plus_width_times_height_times_900,
)

SAMPLES = _REPO / "samples" / "by-format"
_XCF = str(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")


class TestXcfFileSizeMod127Times1950PlusImageTypeTimes2300PlusWidthTimes220PlusHeightTimes190:
    def test_returns_int(self):
        result = xcf_file_size_mod_127_times_1950_plus_image_type_times_2300_plus_width_times_220_plus_height_times_190(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_mod_127_times_1950_plus_image_type_times_2300_plus_width_times_220_plus_height_times_190(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_mod_127_times_1950_plus_image_type_times_2300_plus_width_times_220_plus_height_times_190(_XCF)
        assert result == 99860

    def test_string_path(self):
        result = xcf_file_size_mod_127_times_1950_plus_image_type_times_2300_plus_width_times_220_plus_height_times_190(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_mod_127_times_1950_plus_image_type_times_2300_plus_width_times_220_plus_height_times_190(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)


class TestXcfFileSizeTimes26PlusImageTypeTimes2600PlusWidthTimesHeightTimes900:
    def test_returns_int(self):
        result = xcf_file_size_times_26_plus_image_type_times_2600_plus_width_times_height_times_900(_XCF)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = xcf_file_size_times_26_plus_image_type_times_2600_plus_width_times_height_times_900(_XCF)
        assert result >= 0

    def test_expected_value(self):
        result = xcf_file_size_times_26_plus_image_type_times_2600_plus_width_times_height_times_900(_XCF)
        assert result == 5528

    def test_string_path(self):
        result = xcf_file_size_times_26_plus_image_type_times_2600_plus_width_times_height_times_900(str(_XCF))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = xcf_file_size_times_26_plus_image_type_times_2600_plus_width_times_height_times_900(SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf")
        assert isinstance(result, int)
