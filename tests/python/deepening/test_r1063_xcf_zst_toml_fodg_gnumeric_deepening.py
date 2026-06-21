"""Sprint 510 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_463_times_7800_plus_image_type_times_9700_plus_width_times_960_plus_height_times_930,
    xcf_file_size_times_181_plus_image_type_times_11800_plus_width_times_height_times_6800,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 1390290
FN2_EXPECTED = 39018


class TestXcfFileSizeMod463Times7800PlusImageTypeTimes9700PlusWidthTimes960PlusHeightTimes930:
    def test_returns_int(self):
        result = xcf_file_size_mod_463_times_7800_plus_image_type_times_9700_plus_width_times_960_plus_height_times_930(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_463_times_7800_plus_image_type_times_9700_plus_width_times_960_plus_height_times_930(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_463_times_7800_plus_image_type_times_9700_plus_width_times_960_plus_height_times_930(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_463_times_7800_plus_image_type_times_9700_plus_width_times_960_plus_height_times_930(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_463_times_7800_plus_image_type_times_9700_plus_width_times_960_plus_height_times_930(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes181PlusImageTypeTimes11800PlusWidthTimesHeightTimes6800:
    def test_returns_int(self):
        result = xcf_file_size_times_181_plus_image_type_times_11800_plus_width_times_height_times_6800(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_181_plus_image_type_times_11800_plus_width_times_height_times_6800(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_181_plus_image_type_times_11800_plus_width_times_height_times_6800(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_181_plus_image_type_times_11800_plus_width_times_height_times_6800(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_181_plus_image_type_times_11800_plus_width_times_height_times_6800(_SAMPLE)
        assert result == FN2_EXPECTED
