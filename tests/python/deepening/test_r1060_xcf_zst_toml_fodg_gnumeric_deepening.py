"""Sprint 507 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_461_times_7700_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920,
    xcf_file_size_times_179_plus_image_type_times_11700_plus_width_times_height_times_6700,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 1372470
FN2_EXPECTED = 38562


class TestXcfFileSizeMod461Times7700PlusImageTypeTimes9600PlusWidthTimes950PlusHeightTimes920:
    def test_returns_int(self):
        result = xcf_file_size_mod_461_times_7700_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_461_times_7700_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_461_times_7700_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_461_times_7700_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_461_times_7700_plus_image_type_times_9600_plus_width_times_950_plus_height_times_920(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes179PlusImageTypeTimes11700PlusWidthTimesHeightTimes6700:
    def test_returns_int(self):
        result = xcf_file_size_times_179_plus_image_type_times_11700_plus_width_times_height_times_6700(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_179_plus_image_type_times_11700_plus_width_times_height_times_6700(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_179_plus_image_type_times_11700_plus_width_times_height_times_6700(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_179_plus_image_type_times_11700_plus_width_times_height_times_6700(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_179_plus_image_type_times_11700_plus_width_times_height_times_6700(_SAMPLE)
        assert result == FN2_EXPECTED
