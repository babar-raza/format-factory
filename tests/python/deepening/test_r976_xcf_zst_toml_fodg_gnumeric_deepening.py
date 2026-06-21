"""Sprint 423 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_303_times_4600_plus_image_type_times_6600_plus_width_times_650_plus_height_times_620,
    xcf_file_size_times_111_plus_image_type_times_7100_plus_width_times_height_times_3600,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 820070
FN2_EXPECTED = 23358


class TestXcfFileSizeMod303Times4600PlusImageTypeTimes6600PlusWidthTimes650PlusHeightTimes620:
    def test_returns_int(self):
        result = xcf_file_size_mod_303_times_4600_plus_image_type_times_6600_plus_width_times_650_plus_height_times_620(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_303_times_4600_plus_image_type_times_6600_plus_width_times_650_plus_height_times_620(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_303_times_4600_plus_image_type_times_6600_plus_width_times_650_plus_height_times_620(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_303_times_4600_plus_image_type_times_6600_plus_width_times_650_plus_height_times_620(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_303_times_4600_plus_image_type_times_6600_plus_width_times_650_plus_height_times_620(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes111PlusImageTypeTimes7100PlusWidthTimesHeightTimes3600:
    def test_returns_int(self):
        result = xcf_file_size_times_111_plus_image_type_times_7100_plus_width_times_height_times_3600(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_111_plus_image_type_times_7100_plus_width_times_height_times_3600(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_111_plus_image_type_times_7100_plus_width_times_height_times_3600(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_111_plus_image_type_times_7100_plus_width_times_height_times_3600(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_111_plus_image_type_times_7100_plus_width_times_height_times_3600(_SAMPLE)
        assert result == FN2_EXPECTED
