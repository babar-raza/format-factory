"""Sprint 471 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_373_times_6200_plus_image_type_times_8200_plus_width_times_810_plus_height_times_780,
    xcf_file_size_times_149_plus_image_type_times_10200_plus_width_times_height_times_5300,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 1105190
FN2_EXPECTED = 31822


class TestXcfFileSizeMod373Times6200PlusImageTypeTimes8200PlusWidthTimes810PlusHeightTimes780:
    def test_returns_int(self):
        result = xcf_file_size_mod_373_times_6200_plus_image_type_times_8200_plus_width_times_810_plus_height_times_780(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_373_times_6200_plus_image_type_times_8200_plus_width_times_810_plus_height_times_780(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_373_times_6200_plus_image_type_times_8200_plus_width_times_810_plus_height_times_780(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_373_times_6200_plus_image_type_times_8200_plus_width_times_810_plus_height_times_780(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_373_times_6200_plus_image_type_times_8200_plus_width_times_810_plus_height_times_780(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes149PlusImageTypeTimes10200PlusWidthTimesHeightTimes5300:
    def test_returns_int(self):
        result = xcf_file_size_times_149_plus_image_type_times_10200_plus_width_times_height_times_5300(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_149_plus_image_type_times_10200_plus_width_times_height_times_5300(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_149_plus_image_type_times_10200_plus_width_times_height_times_5300(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_149_plus_image_type_times_10200_plus_width_times_height_times_5300(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_149_plus_image_type_times_10200_plus_width_times_height_times_5300(_SAMPLE)
        assert result == FN2_EXPECTED
