"""Sprint 447 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_347_times_5800_plus_image_type_times_7800_plus_width_times_770_plus_height_times_740,
    xcf_file_size_times_141_plus_image_type_times_9700_plus_width_times_height_times_4900,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 1033910
FN2_EXPECTED = 29998


class TestXcfFileSizeMod347Times5800PlusImageTypeTimes7800PlusWidthTimes770PlusHeightTimes740:
    def test_returns_int(self):
        result = xcf_file_size_mod_347_times_5800_plus_image_type_times_7800_plus_width_times_770_plus_height_times_740(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_347_times_5800_plus_image_type_times_7800_plus_width_times_770_plus_height_times_740(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_347_times_5800_plus_image_type_times_7800_plus_width_times_770_plus_height_times_740(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_347_times_5800_plus_image_type_times_7800_plus_width_times_770_plus_height_times_740(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_347_times_5800_plus_image_type_times_7800_plus_width_times_770_plus_height_times_740(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes141PlusImageTypeTimes9700PlusWidthTimesHeightTimes4900:
    def test_returns_int(self):
        result = xcf_file_size_times_141_plus_image_type_times_9700_plus_width_times_height_times_4900(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_141_plus_image_type_times_9700_plus_width_times_height_times_4900(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_141_plus_image_type_times_9700_plus_width_times_height_times_4900(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_141_plus_image_type_times_9700_plus_width_times_height_times_4900(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_141_plus_image_type_times_9700_plus_width_times_height_times_4900(_SAMPLE)
        assert result == FN2_EXPECTED
