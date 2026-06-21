"""Sprint 501 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_443_times_7400_plus_image_type_times_9400_plus_width_times_930_plus_height_times_900,
    xcf_file_size_times_173_plus_image_type_times_11400_plus_width_times_height_times_6500,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 1319030
FN2_EXPECTED = 37294


class TestXcfFileSizeMod443Times7400PlusImageTypeTimes9400PlusWidthTimes930PlusHeightTimes900:
    def test_returns_int(self):
        result = xcf_file_size_mod_443_times_7400_plus_image_type_times_9400_plus_width_times_930_plus_height_times_900(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_443_times_7400_plus_image_type_times_9400_plus_width_times_930_plus_height_times_900(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_443_times_7400_plus_image_type_times_9400_plus_width_times_930_plus_height_times_900(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_443_times_7400_plus_image_type_times_9400_plus_width_times_930_plus_height_times_900(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_443_times_7400_plus_image_type_times_9400_plus_width_times_930_plus_height_times_900(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes173PlusImageTypeTimes11400PlusWidthTimesHeightTimes6500:
    def test_returns_int(self):
        result = xcf_file_size_times_173_plus_image_type_times_11400_plus_width_times_height_times_6500(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_173_plus_image_type_times_11400_plus_width_times_height_times_6500(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_173_plus_image_type_times_11400_plus_width_times_height_times_6500(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_173_plus_image_type_times_11400_plus_width_times_height_times_6500(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_173_plus_image_type_times_11400_plus_width_times_height_times_6500(_SAMPLE)
        assert result == FN2_EXPECTED
