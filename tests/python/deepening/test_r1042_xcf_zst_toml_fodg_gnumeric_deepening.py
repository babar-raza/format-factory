"""Sprint 489 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_421_times_7000_plus_image_type_times_9000_plus_width_times_890_plus_height_times_860,
    xcf_file_size_times_165_plus_image_type_times_11000_plus_width_times_height_times_6100,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 1247750
FN2_EXPECTED = 35470


class TestXcfFileSizeMod421Times7000PlusImageTypeTimes9000PlusWidthTimes890PlusHeightTimes860:
    def test_returns_int(self):
        result = xcf_file_size_mod_421_times_7000_plus_image_type_times_9000_plus_width_times_890_plus_height_times_860(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_421_times_7000_plus_image_type_times_9000_plus_width_times_890_plus_height_times_860(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_421_times_7000_plus_image_type_times_9000_plus_width_times_890_plus_height_times_860(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_421_times_7000_plus_image_type_times_9000_plus_width_times_890_plus_height_times_860(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_421_times_7000_plus_image_type_times_9000_plus_width_times_890_plus_height_times_860(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes165PlusImageTypeTimes11000PlusWidthTimesHeightTimes6100:
    def test_returns_int(self):
        result = xcf_file_size_times_165_plus_image_type_times_11000_plus_width_times_height_times_6100(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_165_plus_image_type_times_11000_plus_width_times_height_times_6100(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_165_plus_image_type_times_11000_plus_width_times_height_times_6100(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_165_plus_image_type_times_11000_plus_width_times_height_times_6100(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_165_plus_image_type_times_11000_plus_width_times_height_times_6100(_SAMPLE)
        assert result == FN2_EXPECTED
