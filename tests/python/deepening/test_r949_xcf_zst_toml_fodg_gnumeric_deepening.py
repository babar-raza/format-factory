"""Sprint 396 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_279_times_3700_plus_image_type_times_5700_plus_width_times_560_plus_height_times_530,
    xcf_file_size_times_93_plus_image_type_times_6100_plus_width_times_height_times_2700,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 659690
FN2_EXPECTED = 19254


class TestXcfFileSizeMod279Times3700PlusImageTypeTimes5700PlusWidthTimes560PlusHeightTimes530:
    def test_returns_int(self):
        result = xcf_file_size_mod_279_times_3700_plus_image_type_times_5700_plus_width_times_560_plus_height_times_530(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_279_times_3700_plus_image_type_times_5700_plus_width_times_560_plus_height_times_530(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_279_times_3700_plus_image_type_times_5700_plus_width_times_560_plus_height_times_530(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_279_times_3700_plus_image_type_times_5700_plus_width_times_560_plus_height_times_530(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_279_times_3700_plus_image_type_times_5700_plus_width_times_560_plus_height_times_530(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes93PlusImageTypeTimes6100PlusWidthTimesHeightTimes2700:
    def test_returns_int(self):
        result = xcf_file_size_times_93_plus_image_type_times_6100_plus_width_times_height_times_2700(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_93_plus_image_type_times_6100_plus_width_times_height_times_2700(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_93_plus_image_type_times_6100_plus_width_times_height_times_2700(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_93_plus_image_type_times_6100_plus_width_times_height_times_2700(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_93_plus_image_type_times_6100_plus_width_times_height_times_2700(_SAMPLE)
        assert result == FN2_EXPECTED
