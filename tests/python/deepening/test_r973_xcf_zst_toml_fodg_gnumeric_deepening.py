"""Sprint 420 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_301_times_4500_plus_image_type_times_6500_plus_width_times_640_plus_height_times_610,
    xcf_file_size_times_109_plus_image_type_times_6900_plus_width_times_height_times_3500,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 802250
FN2_EXPECTED = 22902


class TestXcfFileSizeMod301Times4500PlusImageTypeTimes6500PlusWidthTimes640PlusHeightTimes610:
    def test_returns_int(self):
        result = xcf_file_size_mod_301_times_4500_plus_image_type_times_6500_plus_width_times_640_plus_height_times_610(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_301_times_4500_plus_image_type_times_6500_plus_width_times_640_plus_height_times_610(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_301_times_4500_plus_image_type_times_6500_plus_width_times_640_plus_height_times_610(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_301_times_4500_plus_image_type_times_6500_plus_width_times_640_plus_height_times_610(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_301_times_4500_plus_image_type_times_6500_plus_width_times_640_plus_height_times_610(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes109PlusImageTypeTimes6900PlusWidthTimesHeightTimes3500:
    def test_returns_int(self):
        result = xcf_file_size_times_109_plus_image_type_times_6900_plus_width_times_height_times_3500(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_109_plus_image_type_times_6900_plus_width_times_height_times_3500(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_109_plus_image_type_times_6900_plus_width_times_height_times_3500(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_109_plus_image_type_times_6900_plus_width_times_height_times_3500(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_109_plus_image_type_times_6900_plus_width_times_height_times_3500(_SAMPLE)
        assert result == FN2_EXPECTED
