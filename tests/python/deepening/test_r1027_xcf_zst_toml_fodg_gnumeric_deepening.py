"""Sprint 474 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_379_times_6300_plus_image_type_times_8300_plus_width_times_820_plus_height_times_790,
    xcf_file_size_times_151_plus_image_type_times_10300_plus_width_times_height_times_5400,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 1123010
FN2_EXPECTED = 32278


class TestXcfFileSizeMod379Times6300PlusImageTypeTimes8300PlusWidthTimes820PlusHeightTimes790:
    def test_returns_int(self):
        result = xcf_file_size_mod_379_times_6300_plus_image_type_times_8300_plus_width_times_820_plus_height_times_790(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_379_times_6300_plus_image_type_times_8300_plus_width_times_820_plus_height_times_790(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_379_times_6300_plus_image_type_times_8300_plus_width_times_820_plus_height_times_790(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_379_times_6300_plus_image_type_times_8300_plus_width_times_820_plus_height_times_790(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_379_times_6300_plus_image_type_times_8300_plus_width_times_820_plus_height_times_790(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes151PlusImageTypeTimes10300PlusWidthTimesHeightTimes5400:
    def test_returns_int(self):
        result = xcf_file_size_times_151_plus_image_type_times_10300_plus_width_times_height_times_5400(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_151_plus_image_type_times_10300_plus_width_times_height_times_5400(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_151_plus_image_type_times_10300_plus_width_times_height_times_5400(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_151_plus_image_type_times_10300_plus_width_times_height_times_5400(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_151_plus_image_type_times_10300_plus_width_times_height_times_5400(_SAMPLE)
        assert result == FN2_EXPECTED
