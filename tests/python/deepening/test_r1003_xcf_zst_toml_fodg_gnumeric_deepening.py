"""Sprint 450 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_383_times_6400_plus_image_type_times_8400_plus_width_times_830_plus_height_times_800,
    xcf_file_size_times_153_plus_image_type_times_10500_plus_width_times_height_times_5500,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 1140830
FN2_EXPECTED = 32734


class TestXcfFileSizeMod383Times6400PlusImageTypeTimes8400PlusWidthTimes830PlusHeightTimes800:
    def test_returns_int(self):
        result = xcf_file_size_mod_383_times_6400_plus_image_type_times_8400_plus_width_times_830_plus_height_times_800(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_383_times_6400_plus_image_type_times_8400_plus_width_times_830_plus_height_times_800(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_383_times_6400_plus_image_type_times_8400_plus_width_times_830_plus_height_times_800(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_383_times_6400_plus_image_type_times_8400_plus_width_times_830_plus_height_times_800(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_383_times_6400_plus_image_type_times_8400_plus_width_times_830_plus_height_times_800(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes153PlusImageTypeTimes10500PlusWidthTimesHeightTimes5500:
    def test_returns_int(self):
        result = xcf_file_size_times_153_plus_image_type_times_10500_plus_width_times_height_times_5500(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_153_plus_image_type_times_10500_plus_width_times_height_times_5500(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_153_plus_image_type_times_10500_plus_width_times_height_times_5500(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_153_plus_image_type_times_10500_plus_width_times_height_times_5500(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_153_plus_image_type_times_10500_plus_width_times_height_times_5500(_SAMPLE)
        assert result == FN2_EXPECTED
