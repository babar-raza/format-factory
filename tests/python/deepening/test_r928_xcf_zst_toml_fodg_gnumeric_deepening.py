"""Sprint 375 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_249_times_3250_plus_image_type_times_4800_plus_width_times_480_plus_height_times_450,
    xcf_file_size_times_77_plus_image_type_times_5300_plus_width_times_height_times_2250,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 579430
FN2_EXPECTED = 15956


class TestXcfFileSizeMod249Times3250PlusImageTypeTimes4800PlusWidthTimes480PlusHeightTimes450:
    def test_returns_int(self):
        result = xcf_file_size_mod_249_times_3250_plus_image_type_times_4800_plus_width_times_480_plus_height_times_450(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_249_times_3250_plus_image_type_times_4800_plus_width_times_480_plus_height_times_450(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_249_times_3250_plus_image_type_times_4800_plus_width_times_480_plus_height_times_450(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_249_times_3250_plus_image_type_times_4800_plus_width_times_480_plus_height_times_450(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_249_times_3250_plus_image_type_times_4800_plus_width_times_480_plus_height_times_450(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes77PlusImageTypeTimes5300PlusWidthTimesHeightTimes2250:
    def test_returns_int(self):
        result = xcf_file_size_times_77_plus_image_type_times_5300_plus_width_times_height_times_2250(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_77_plus_image_type_times_5300_plus_width_times_height_times_2250(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_77_plus_image_type_times_5300_plus_width_times_height_times_2250(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_77_plus_image_type_times_5300_plus_width_times_height_times_2250(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_77_plus_image_type_times_5300_plus_width_times_height_times_2250(_SAMPLE)
        assert result == FN2_EXPECTED
