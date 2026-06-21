"""Sprint 351 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_213_times_2850_plus_image_type_times_4000_plus_width_times_400_plus_height_times_370,
    xcf_file_size_times_59_plus_image_type_times_4400_plus_width_times_height_times_1800,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 508070
FN2_EXPECTED = 12302


class TestXcfFileSizeMod213Times2850PlusImageTypeTimes4000PlusWidthTimes400PlusHeightTimes370:
    def test_returns_int(self):
        result = xcf_file_size_mod_213_times_2850_plus_image_type_times_4000_plus_width_times_400_plus_height_times_370(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_213_times_2850_plus_image_type_times_4000_plus_width_times_400_plus_height_times_370(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_213_times_2850_plus_image_type_times_4000_plus_width_times_400_plus_height_times_370(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_213_times_2850_plus_image_type_times_4000_plus_width_times_400_plus_height_times_370(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_213_times_2850_plus_image_type_times_4000_plus_width_times_400_plus_height_times_370(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes59PlusImageTypeTimes4400PlusWidthTimesHeightTimes1800:
    def test_returns_int(self):
        result = xcf_file_size_times_59_plus_image_type_times_4400_plus_width_times_height_times_1800(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_59_plus_image_type_times_4400_plus_width_times_height_times_1800(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_59_plus_image_type_times_4400_plus_width_times_height_times_1800(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_59_plus_image_type_times_4400_plus_width_times_height_times_1800(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_59_plus_image_type_times_4400_plus_width_times_height_times_1800(_SAMPLE)
        assert result == FN2_EXPECTED
