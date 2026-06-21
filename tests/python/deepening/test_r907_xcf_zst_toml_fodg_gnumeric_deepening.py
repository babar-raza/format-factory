"""Sprint 354 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_217_times_2900_plus_image_type_times_4100_plus_width_times_410_plus_height_times_380,
    xcf_file_size_times_61_plus_image_type_times_4500_plus_width_times_height_times_1850,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 516990
FN2_EXPECTED = 12708


class TestXcfFileSizeMod217Times2900PlusImageTypeTimes4100PlusWidthTimes410PlusHeightTimes380:
    def test_returns_int(self):
        result = xcf_file_size_mod_217_times_2900_plus_image_type_times_4100_plus_width_times_410_plus_height_times_380(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_217_times_2900_plus_image_type_times_4100_plus_width_times_410_plus_height_times_380(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_217_times_2900_plus_image_type_times_4100_plus_width_times_410_plus_height_times_380(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_217_times_2900_plus_image_type_times_4100_plus_width_times_410_plus_height_times_380(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_217_times_2900_plus_image_type_times_4100_plus_width_times_410_plus_height_times_380(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes61PlusImageTypeTimes4500PlusWidthTimesHeightTimes1850:
    def test_returns_int(self):
        result = xcf_file_size_times_61_plus_image_type_times_4500_plus_width_times_height_times_1850(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_61_plus_image_type_times_4500_plus_width_times_height_times_1850(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_61_plus_image_type_times_4500_plus_width_times_height_times_1850(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_61_plus_image_type_times_4500_plus_width_times_height_times_1850(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_61_plus_image_type_times_4500_plus_width_times_height_times_1850(_SAMPLE)
        assert result == FN2_EXPECTED
