"""Sprint 411 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_295_times_4200_plus_image_type_times_6200_plus_width_times_610_plus_height_times_580,
    xcf_file_size_times_103_plus_image_type_times_6600_plus_width_times_height_times_3200,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 748790
FN2_EXPECTED = 21534


class TestXcfFileSizeMod295Times4200PlusImageTypeTimes6200PlusWidthTimes610PlusHeightTimes580:
    def test_returns_int(self):
        result = xcf_file_size_mod_295_times_4200_plus_image_type_times_6200_plus_width_times_610_plus_height_times_580(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_295_times_4200_plus_image_type_times_6200_plus_width_times_610_plus_height_times_580(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_295_times_4200_plus_image_type_times_6200_plus_width_times_610_plus_height_times_580(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_295_times_4200_plus_image_type_times_6200_plus_width_times_610_plus_height_times_580(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_295_times_4200_plus_image_type_times_6200_plus_width_times_610_plus_height_times_580(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes103PlusImageTypeTimes6600PlusWidthTimesHeightTimes3200:
    def test_returns_int(self):
        result = xcf_file_size_times_103_plus_image_type_times_6600_plus_width_times_height_times_3200(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_103_plus_image_type_times_6600_plus_width_times_height_times_3200(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_103_plus_image_type_times_6600_plus_width_times_height_times_3200(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_103_plus_image_type_times_6600_plus_width_times_height_times_3200(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_103_plus_image_type_times_6600_plus_width_times_height_times_3200(_SAMPLE)
        assert result == FN2_EXPECTED
