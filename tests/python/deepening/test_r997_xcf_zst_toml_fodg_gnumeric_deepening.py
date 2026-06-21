"""Sprint 444 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_319_times_5300_plus_image_type_times_7300_plus_width_times_720_plus_height_times_690,
    xcf_file_size_times_129_plus_image_type_times_8500_plus_width_times_height_times_4300,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 944810
FN2_EXPECTED = 27262


class TestXcfFileSizeMod319Times5300PlusImageTypeTimes7300PlusWidthTimes720PlusHeightTimes690:
    def test_returns_int(self):
        result = xcf_file_size_mod_319_times_5300_plus_image_type_times_7300_plus_width_times_720_plus_height_times_690(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_319_times_5300_plus_image_type_times_7300_plus_width_times_720_plus_height_times_690(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_319_times_5300_plus_image_type_times_7300_plus_width_times_720_plus_height_times_690(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_319_times_5300_plus_image_type_times_7300_plus_width_times_720_plus_height_times_690(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_319_times_5300_plus_image_type_times_7300_plus_width_times_720_plus_height_times_690(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes129PlusImageTypeTimes8500PlusWidthTimesHeightTimes4300:
    def test_returns_int(self):
        result = xcf_file_size_times_129_plus_image_type_times_8500_plus_width_times_height_times_4300(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_129_plus_image_type_times_8500_plus_width_times_height_times_4300(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_129_plus_image_type_times_8500_plus_width_times_height_times_4300(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_129_plus_image_type_times_8500_plus_width_times_height_times_4300(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_129_plus_image_type_times_8500_plus_width_times_height_times_4300(_SAMPLE)
        assert result == FN2_EXPECTED
