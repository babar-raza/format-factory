"""Sprint 414 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_297_times_4300_plus_image_type_times_6300_plus_width_times_620_plus_height_times_590,
    xcf_file_size_times_105_plus_image_type_times_6700_plus_width_times_height_times_3300,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 766610
FN2_EXPECTED = 21990


class TestXcfFileSizeMod297Times4300PlusImageTypeTimes6300PlusWidthTimes620PlusHeightTimes590:
    def test_returns_int(self):
        result = xcf_file_size_mod_297_times_4300_plus_image_type_times_6300_plus_width_times_620_plus_height_times_590(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_297_times_4300_plus_image_type_times_6300_plus_width_times_620_plus_height_times_590(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_297_times_4300_plus_image_type_times_6300_plus_width_times_620_plus_height_times_590(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_297_times_4300_plus_image_type_times_6300_plus_width_times_620_plus_height_times_590(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_297_times_4300_plus_image_type_times_6300_plus_width_times_620_plus_height_times_590(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes105PlusImageTypeTimes6700PlusWidthTimesHeightTimes3300:
    def test_returns_int(self):
        result = xcf_file_size_times_105_plus_image_type_times_6700_plus_width_times_height_times_3300(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_105_plus_image_type_times_6700_plus_width_times_height_times_3300(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_105_plus_image_type_times_6700_plus_width_times_height_times_3300(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_105_plus_image_type_times_6700_plus_width_times_height_times_3300(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_105_plus_image_type_times_6700_plus_width_times_height_times_3300(_SAMPLE)
        assert result == FN2_EXPECTED
