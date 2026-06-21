"""Sprint 435 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_311_times_5000_plus_image_type_times_7000_plus_width_times_690_plus_height_times_660,
    xcf_file_size_times_121_plus_image_type_times_7900_plus_width_times_height_times_4000,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 891350
FN2_EXPECTED = 25538


class TestXcfFileSizeMod311Times5000PlusImageTypeTimes7000PlusWidthTimes690PlusHeightTimes660:
    def test_returns_int(self):
        result = xcf_file_size_mod_311_times_5000_plus_image_type_times_7000_plus_width_times_690_plus_height_times_660(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_311_times_5000_plus_image_type_times_7000_plus_width_times_690_plus_height_times_660(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_311_times_5000_plus_image_type_times_7000_plus_width_times_690_plus_height_times_660(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_311_times_5000_plus_image_type_times_7000_plus_width_times_690_plus_height_times_660(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_311_times_5000_plus_image_type_times_7000_plus_width_times_690_plus_height_times_660(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes121PlusImageTypeTimes7900PlusWidthTimesHeightTimes4000:
    def test_returns_int(self):
        result = xcf_file_size_times_121_plus_image_type_times_7900_plus_width_times_height_times_4000(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_121_plus_image_type_times_7900_plus_width_times_height_times_4000(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_121_plus_image_type_times_7900_plus_width_times_height_times_4000(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_121_plus_image_type_times_7900_plus_width_times_height_times_4000(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_121_plus_image_type_times_7900_plus_width_times_height_times_4000(_SAMPLE)
        assert result == FN2_EXPECTED
