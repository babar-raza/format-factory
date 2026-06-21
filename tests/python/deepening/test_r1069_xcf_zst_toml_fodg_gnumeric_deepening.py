"""Sprint 516 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_479_times_8000_plus_image_type_times_9900_plus_width_times_980_plus_height_times_950,
    xcf_file_size_times_185_plus_image_type_times_12000_plus_width_times_height_times_7000,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 1425930
FN2_EXPECTED = 39930


class TestXcfFileSizeMod479Times8000PlusImageTypeTimes9900PlusWidthTimes980PlusHeightTimes950:
    def test_returns_int(self):
        result = xcf_file_size_mod_479_times_8000_plus_image_type_times_9900_plus_width_times_980_plus_height_times_950(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_479_times_8000_plus_image_type_times_9900_plus_width_times_980_plus_height_times_950(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_479_times_8000_plus_image_type_times_9900_plus_width_times_980_plus_height_times_950(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_479_times_8000_plus_image_type_times_9900_plus_width_times_980_plus_height_times_950(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_479_times_8000_plus_image_type_times_9900_plus_width_times_980_plus_height_times_950(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes185PlusImageTypeTimes12000PlusWidthTimesHeightTimes7000:
    def test_returns_int(self):
        result = xcf_file_size_times_185_plus_image_type_times_12000_plus_width_times_height_times_7000(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_185_plus_image_type_times_12000_plus_width_times_height_times_7000(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_185_plus_image_type_times_12000_plus_width_times_height_times_7000(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_185_plus_image_type_times_12000_plus_width_times_height_times_7000(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_185_plus_image_type_times_12000_plus_width_times_height_times_7000(_SAMPLE)
        assert result == FN2_EXPECTED
