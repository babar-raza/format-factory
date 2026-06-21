"""Sprint 378 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_251_times_3300_plus_image_type_times_4900_plus_width_times_490_plus_height_times_460,
    xcf_file_size_times_79_plus_image_type_times_5400_plus_width_times_height_times_2300,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 588350
FN2_EXPECTED = 16362


class TestXcfFileSizeMod251Times3300PlusImageTypeTimes4900PlusWidthTimes490PlusHeightTimes460:
    def test_returns_int(self):
        result = xcf_file_size_mod_251_times_3300_plus_image_type_times_4900_plus_width_times_490_plus_height_times_460(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_251_times_3300_plus_image_type_times_4900_plus_width_times_490_plus_height_times_460(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_251_times_3300_plus_image_type_times_4900_plus_width_times_490_plus_height_times_460(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_251_times_3300_plus_image_type_times_4900_plus_width_times_490_plus_height_times_460(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_251_times_3300_plus_image_type_times_4900_plus_width_times_490_plus_height_times_460(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes79PlusImageTypeTimes5400PlusWidthTimesHeightTimes2300:
    def test_returns_int(self):
        result = xcf_file_size_times_79_plus_image_type_times_5400_plus_width_times_height_times_2300(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_79_plus_image_type_times_5400_plus_width_times_height_times_2300(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_79_plus_image_type_times_5400_plus_width_times_height_times_2300(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_79_plus_image_type_times_5400_plus_width_times_height_times_2300(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_79_plus_image_type_times_5400_plus_width_times_height_times_2300(_SAMPLE)
        assert result == FN2_EXPECTED
