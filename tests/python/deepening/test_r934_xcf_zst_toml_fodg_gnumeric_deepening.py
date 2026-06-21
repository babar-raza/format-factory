"""Sprint 381 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_253_times_3350_plus_image_type_times_5000_plus_width_times_500_plus_height_times_470,
    xcf_file_size_times_81_plus_image_type_times_5500_plus_width_times_height_times_2350,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 597270
FN2_EXPECTED = 16768


class TestXcfFileSizeMod253Times3350PlusImageTypeTimes5000PlusWidthTimes500PlusHeightTimes470:
    def test_returns_int(self):
        result = xcf_file_size_mod_253_times_3350_plus_image_type_times_5000_plus_width_times_500_plus_height_times_470(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_253_times_3350_plus_image_type_times_5000_plus_width_times_500_plus_height_times_470(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_253_times_3350_plus_image_type_times_5000_plus_width_times_500_plus_height_times_470(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_253_times_3350_plus_image_type_times_5000_plus_width_times_500_plus_height_times_470(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_253_times_3350_plus_image_type_times_5000_plus_width_times_500_plus_height_times_470(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes81PlusImageTypeTimes5500PlusWidthTimesHeightTimes2350:
    def test_returns_int(self):
        result = xcf_file_size_times_81_plus_image_type_times_5500_plus_width_times_height_times_2350(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_81_plus_image_type_times_5500_plus_width_times_height_times_2350(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_81_plus_image_type_times_5500_plus_width_times_height_times_2350(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_81_plus_image_type_times_5500_plus_width_times_height_times_2350(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_81_plus_image_type_times_5500_plus_width_times_height_times_2350(_SAMPLE)
        assert result == FN2_EXPECTED
