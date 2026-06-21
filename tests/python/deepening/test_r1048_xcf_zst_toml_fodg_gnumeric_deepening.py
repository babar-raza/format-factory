"""Sprint 495 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_433_times_7200_plus_image_type_times_9200_plus_width_times_910_plus_height_times_880,
    xcf_file_size_times_169_plus_image_type_times_11200_plus_width_times_height_times_6300,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 1283390
FN2_EXPECTED = 36382


class TestXcfFileSizeMod433Times7200PlusImageTypeTimes9200PlusWidthTimes910PlusHeightTimes880:
    def test_returns_int(self):
        result = xcf_file_size_mod_433_times_7200_plus_image_type_times_9200_plus_width_times_910_plus_height_times_880(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_433_times_7200_plus_image_type_times_9200_plus_width_times_910_plus_height_times_880(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_433_times_7200_plus_image_type_times_9200_plus_width_times_910_plus_height_times_880(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_433_times_7200_plus_image_type_times_9200_plus_width_times_910_plus_height_times_880(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_433_times_7200_plus_image_type_times_9200_plus_width_times_910_plus_height_times_880(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes169PlusImageTypeTimes11200PlusWidthTimesHeightTimes6300:
    def test_returns_int(self):
        result = xcf_file_size_times_169_plus_image_type_times_11200_plus_width_times_height_times_6300(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_169_plus_image_type_times_11200_plus_width_times_height_times_6300(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_169_plus_image_type_times_11200_plus_width_times_height_times_6300(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_169_plus_image_type_times_11200_plus_width_times_height_times_6300(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_169_plus_image_type_times_11200_plus_width_times_height_times_6300(_SAMPLE)
        assert result == FN2_EXPECTED
