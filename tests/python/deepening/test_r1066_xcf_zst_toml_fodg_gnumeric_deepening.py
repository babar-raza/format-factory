"""Sprint 513 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_467_times_7900_plus_image_type_times_9800_plus_width_times_970_plus_height_times_940,
    xcf_file_size_times_183_plus_image_type_times_11900_plus_width_times_height_times_6900,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 1408110
FN2_EXPECTED = 39474


class TestXcfFileSizeMod467Times7900PlusImageTypeTimes9800PlusWidthTimes970PlusHeightTimes940:
    def test_returns_int(self):
        result = xcf_file_size_mod_467_times_7900_plus_image_type_times_9800_plus_width_times_970_plus_height_times_940(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_467_times_7900_plus_image_type_times_9800_plus_width_times_970_plus_height_times_940(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_467_times_7900_plus_image_type_times_9800_plus_width_times_970_plus_height_times_940(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_467_times_7900_plus_image_type_times_9800_plus_width_times_970_plus_height_times_940(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_467_times_7900_plus_image_type_times_9800_plus_width_times_970_plus_height_times_940(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes183PlusImageTypeTimes11900PlusWidthTimesHeightTimes6900:
    def test_returns_int(self):
        result = xcf_file_size_times_183_plus_image_type_times_11900_plus_width_times_height_times_6900(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_183_plus_image_type_times_11900_plus_width_times_height_times_6900(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_183_plus_image_type_times_11900_plus_width_times_height_times_6900(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_183_plus_image_type_times_11900_plus_width_times_height_times_6900(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_183_plus_image_type_times_11900_plus_width_times_height_times_6900(_SAMPLE)
        assert result == FN2_EXPECTED
