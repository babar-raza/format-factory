"""Sprint 522 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_499_times_8400_plus_image_type_times_10300_plus_width_times_1020_plus_height_times_990,
    xcf_file_size_times_191_plus_image_type_times_12300_plus_width_times_height_times_7300,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-red-rgb.xcf"

FN1_EXPECTED = 1488810
FN2_EXPECTED = 41107


class TestXcfFileSizeMod499Times8400PlusImageTypeTimes10300PlusWidthTimes1020PlusHeightTimes990:
    def test_returns_int(self):
        result = xcf_file_size_mod_499_times_8400_plus_image_type_times_10300_plus_width_times_1020_plus_height_times_990(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_499_times_8400_plus_image_type_times_10300_plus_width_times_1020_plus_height_times_990(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_499_times_8400_plus_image_type_times_10300_plus_width_times_1020_plus_height_times_990(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_499_times_8400_plus_image_type_times_10300_plus_width_times_1020_plus_height_times_990(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_499_times_8400_plus_image_type_times_10300_plus_width_times_1020_plus_height_times_990(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes191PlusImageTypeTimes12300PlusWidthTimesHeightTimes7300:
    def test_returns_int(self):
        result = xcf_file_size_times_191_plus_image_type_times_12300_plus_width_times_height_times_7300(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_191_plus_image_type_times_12300_plus_width_times_height_times_7300(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_191_plus_image_type_times_12300_plus_width_times_height_times_7300(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_191_plus_image_type_times_12300_plus_width_times_height_times_7300(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_191_plus_image_type_times_12300_plus_width_times_height_times_7300(_SAMPLE)
        assert result == FN2_EXPECTED
