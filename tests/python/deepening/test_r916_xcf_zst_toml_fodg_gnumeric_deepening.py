"""Sprint 363 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_229_times_3050_plus_image_type_times_4400_plus_width_times_440_plus_height_times_410,
    xcf_file_size_times_69_plus_image_type_times_4900_plus_width_times_height_times_2050,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 543750
FN2_EXPECTED = 14332


class TestXcfFileSizeMod229Times3050PlusImageTypeTimes4400PlusWidthTimes440PlusHeightTimes410:
    def test_returns_int(self):
        result = xcf_file_size_mod_229_times_3050_plus_image_type_times_4400_plus_width_times_440_plus_height_times_410(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_229_times_3050_plus_image_type_times_4400_plus_width_times_440_plus_height_times_410(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_229_times_3050_plus_image_type_times_4400_plus_width_times_440_plus_height_times_410(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_229_times_3050_plus_image_type_times_4400_plus_width_times_440_plus_height_times_410(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_229_times_3050_plus_image_type_times_4400_plus_width_times_440_plus_height_times_410(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes69PlusImageTypeTimes4900PlusWidthTimesHeightTimes2050:
    def test_returns_int(self):
        result = xcf_file_size_times_69_plus_image_type_times_4900_plus_width_times_height_times_2050(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_69_plus_image_type_times_4900_plus_width_times_height_times_2050(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_69_plus_image_type_times_4900_plus_width_times_height_times_2050(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_69_plus_image_type_times_4900_plus_width_times_height_times_2050(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_69_plus_image_type_times_4900_plus_width_times_height_times_2050(_SAMPLE)
        assert result == FN2_EXPECTED
