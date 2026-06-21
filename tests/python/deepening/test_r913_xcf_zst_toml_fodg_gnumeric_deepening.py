"""Sprint 360 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_225_times_3000_plus_image_type_times_4300_plus_width_times_430_plus_height_times_400,
    xcf_file_size_times_67_plus_image_type_times_4800_plus_width_times_height_times_2000,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 534830
FN2_EXPECTED = 13926


class TestXcfFileSizeMod225Times3000PlusImageTypeTimes4300PlusWidthTimes430PlusHeightTimes400:
    def test_returns_int(self):
        result = xcf_file_size_mod_225_times_3000_plus_image_type_times_4300_plus_width_times_430_plus_height_times_400(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_225_times_3000_plus_image_type_times_4300_plus_width_times_430_plus_height_times_400(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_225_times_3000_plus_image_type_times_4300_plus_width_times_430_plus_height_times_400(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_225_times_3000_plus_image_type_times_4300_plus_width_times_430_plus_height_times_400(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_225_times_3000_plus_image_type_times_4300_plus_width_times_430_plus_height_times_400(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes67PlusImageTypeTimes4800PlusWidthTimesHeightTimes2000:
    def test_returns_int(self):
        result = xcf_file_size_times_67_plus_image_type_times_4800_plus_width_times_height_times_2000(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_67_plus_image_type_times_4800_plus_width_times_height_times_2000(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_67_plus_image_type_times_4800_plus_width_times_height_times_2000(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_67_plus_image_type_times_4800_plus_width_times_height_times_2000(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_67_plus_image_type_times_4800_plus_width_times_height_times_2000(_SAMPLE)
        assert result == FN2_EXPECTED
