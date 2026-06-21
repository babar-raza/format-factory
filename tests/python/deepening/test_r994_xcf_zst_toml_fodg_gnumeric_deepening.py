"""Sprint 441 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_317_times_5200_plus_image_type_times_7200_plus_width_times_710_plus_height_times_680,
    xcf_file_size_times_127_plus_image_type_times_8300_plus_width_times_height_times_4200,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 926990
FN2_EXPECTED = 26806


class TestXcfFileSizeMod317Times5200PlusImageTypeTimes7200PlusWidthTimes710PlusHeightTimes680:
    def test_returns_int(self):
        result = xcf_file_size_mod_317_times_5200_plus_image_type_times_7200_plus_width_times_710_plus_height_times_680(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_317_times_5200_plus_image_type_times_7200_plus_width_times_710_plus_height_times_680(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_317_times_5200_plus_image_type_times_7200_plus_width_times_710_plus_height_times_680(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_317_times_5200_plus_image_type_times_7200_plus_width_times_710_plus_height_times_680(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_317_times_5200_plus_image_type_times_7200_plus_width_times_710_plus_height_times_680(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes127PlusImageTypeTimes8300PlusWidthTimesHeightTimes4200:
    def test_returns_int(self):
        result = xcf_file_size_times_127_plus_image_type_times_8300_plus_width_times_height_times_4200(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_127_plus_image_type_times_8300_plus_width_times_height_times_4200(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_127_plus_image_type_times_8300_plus_width_times_height_times_4200(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_127_plus_image_type_times_8300_plus_width_times_height_times_4200(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_127_plus_image_type_times_8300_plus_width_times_height_times_4200(_SAMPLE)
        assert result == FN2_EXPECTED
