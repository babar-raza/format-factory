"""Sprint 492 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_431_times_7100_plus_image_type_times_9100_plus_width_times_900_plus_height_times_870,
    xcf_file_size_times_167_plus_image_type_times_11100_plus_width_times_height_times_6200,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 1265570
FN2_EXPECTED = 35926


class TestXcfFileSizeMod431Times7100PlusImageTypeTimes9100PlusWidthTimes900PlusHeightTimes870:
    def test_returns_int(self):
        result = xcf_file_size_mod_431_times_7100_plus_image_type_times_9100_plus_width_times_900_plus_height_times_870(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_431_times_7100_plus_image_type_times_9100_plus_width_times_900_plus_height_times_870(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_431_times_7100_plus_image_type_times_9100_plus_width_times_900_plus_height_times_870(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_431_times_7100_plus_image_type_times_9100_plus_width_times_900_plus_height_times_870(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_431_times_7100_plus_image_type_times_9100_plus_width_times_900_plus_height_times_870(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes167PlusImageTypeTimes11100PlusWidthTimesHeightTimes6200:
    def test_returns_int(self):
        result = xcf_file_size_times_167_plus_image_type_times_11100_plus_width_times_height_times_6200(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_167_plus_image_type_times_11100_plus_width_times_height_times_6200(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_167_plus_image_type_times_11100_plus_width_times_height_times_6200(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_167_plus_image_type_times_11100_plus_width_times_height_times_6200(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_167_plus_image_type_times_11100_plus_width_times_height_times_6200(_SAMPLE)
        assert result == FN2_EXPECTED
