"""Sprint 405 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_289_times_4000_plus_image_type_times_6000_plus_width_times_590_plus_height_times_560,
    xcf_file_size_times_99_plus_image_type_times_6400_plus_width_times_height_times_3000,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 713150
FN2_EXPECTED = 20622


class TestXcfFileSizeMod289Times4000PlusImageTypeTimes6000PlusWidthTimes590PlusHeightTimes560:
    def test_returns_int(self):
        result = xcf_file_size_mod_289_times_4000_plus_image_type_times_6000_plus_width_times_590_plus_height_times_560(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_289_times_4000_plus_image_type_times_6000_plus_width_times_590_plus_height_times_560(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_289_times_4000_plus_image_type_times_6000_plus_width_times_590_plus_height_times_560(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_289_times_4000_plus_image_type_times_6000_plus_width_times_590_plus_height_times_560(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_289_times_4000_plus_image_type_times_6000_plus_width_times_590_plus_height_times_560(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes99PlusImageTypeTimes6400PlusWidthTimesHeightTimes3000:
    def test_returns_int(self):
        result = xcf_file_size_times_99_plus_image_type_times_6400_plus_width_times_height_times_3000(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_99_plus_image_type_times_6400_plus_width_times_height_times_3000(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_99_plus_image_type_times_6400_plus_width_times_height_times_3000(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_99_plus_image_type_times_6400_plus_width_times_height_times_3000(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_99_plus_image_type_times_6400_plus_width_times_height_times_3000(_SAMPLE)
        assert result == FN2_EXPECTED
