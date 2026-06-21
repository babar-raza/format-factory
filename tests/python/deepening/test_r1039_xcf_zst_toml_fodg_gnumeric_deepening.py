"""Sprint 486 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_419_times_6900_plus_image_type_times_8900_plus_width_times_880_plus_height_times_850,
    xcf_file_size_times_163_plus_image_type_times_10900_plus_width_times_height_times_6000,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 1229930
FN2_EXPECTED = 35014


class TestXcfFileSizeMod419Times6900PlusImageTypeTimes8900PlusWidthTimes880PlusHeightTimes850:
    def test_returns_int(self):
        result = xcf_file_size_mod_419_times_6900_plus_image_type_times_8900_plus_width_times_880_plus_height_times_850(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_419_times_6900_plus_image_type_times_8900_plus_width_times_880_plus_height_times_850(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_419_times_6900_plus_image_type_times_8900_plus_width_times_880_plus_height_times_850(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_419_times_6900_plus_image_type_times_8900_plus_width_times_880_plus_height_times_850(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_419_times_6900_plus_image_type_times_8900_plus_width_times_880_plus_height_times_850(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes163PlusImageTypeTimes10900PlusWidthTimesHeightTimes6000:
    def test_returns_int(self):
        result = xcf_file_size_times_163_plus_image_type_times_10900_plus_width_times_height_times_6000(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_163_plus_image_type_times_10900_plus_width_times_height_times_6000(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_163_plus_image_type_times_10900_plus_width_times_height_times_6000(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_163_plus_image_type_times_10900_plus_width_times_height_times_6000(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_163_plus_image_type_times_10900_plus_width_times_height_times_6000(_SAMPLE)
        assert result == FN2_EXPECTED
