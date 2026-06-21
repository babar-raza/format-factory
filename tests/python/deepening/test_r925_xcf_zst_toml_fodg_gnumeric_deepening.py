"""Sprint 372 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_247_times_3200_plus_image_type_times_4700_plus_width_times_470_plus_height_times_440,
    xcf_file_size_times_75_plus_image_type_times_5200_plus_width_times_height_times_2200,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 570510
FN2_EXPECTED = 15550


class TestXcfFileSizeMod247Times3200PlusImageTypeTimes4700PlusWidthTimes470PlusHeightTimes440:
    def test_returns_int(self):
        result = xcf_file_size_mod_247_times_3200_plus_image_type_times_4700_plus_width_times_470_plus_height_times_440(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_247_times_3200_plus_image_type_times_4700_plus_width_times_470_plus_height_times_440(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_247_times_3200_plus_image_type_times_4700_plus_width_times_470_plus_height_times_440(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_247_times_3200_plus_image_type_times_4700_plus_width_times_470_plus_height_times_440(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_247_times_3200_plus_image_type_times_4700_plus_width_times_470_plus_height_times_440(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes75PlusImageTypeTimes5200PlusWidthTimesHeightTimes2200:
    def test_returns_int(self):
        result = xcf_file_size_times_75_plus_image_type_times_5200_plus_width_times_height_times_2200(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_75_plus_image_type_times_5200_plus_width_times_height_times_2200(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_75_plus_image_type_times_5200_plus_width_times_height_times_2200(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_75_plus_image_type_times_5200_plus_width_times_height_times_2200(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_75_plus_image_type_times_5200_plus_width_times_height_times_2200(_SAMPLE)
        assert result == FN2_EXPECTED
