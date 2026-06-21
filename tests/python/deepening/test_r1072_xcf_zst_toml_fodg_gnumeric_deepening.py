"""Sprint 519 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_487_times_8100_plus_image_type_times_10000_plus_width_times_990_plus_height_times_960,
    xcf_file_size_times_187_plus_image_type_times_12100_plus_width_times_height_times_7100,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 1443750
FN2_EXPECTED = 40386


class TestXcfFileSizeMod487Times8100PlusImageTypeTimes10000PlusWidthTimes990PlusHeightTimes960:
    def test_returns_int(self):
        result = xcf_file_size_mod_487_times_8100_plus_image_type_times_10000_plus_width_times_990_plus_height_times_960(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_487_times_8100_plus_image_type_times_10000_plus_width_times_990_plus_height_times_960(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_487_times_8100_plus_image_type_times_10000_plus_width_times_990_plus_height_times_960(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_487_times_8100_plus_image_type_times_10000_plus_width_times_990_plus_height_times_960(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_487_times_8100_plus_image_type_times_10000_plus_width_times_990_plus_height_times_960(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes187PlusImageTypeTimes12100PlusWidthTimesHeightTimes7100:
    def test_returns_int(self):
        result = xcf_file_size_times_187_plus_image_type_times_12100_plus_width_times_height_times_7100(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_187_plus_image_type_times_12100_plus_width_times_height_times_7100(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_187_plus_image_type_times_12100_plus_width_times_height_times_7100(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_187_plus_image_type_times_12100_plus_width_times_height_times_7100(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_187_plus_image_type_times_12100_plus_width_times_height_times_7100(_SAMPLE)
        assert result == FN2_EXPECTED
