"""Sprint 384 — XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_257_times_3400_plus_image_type_times_5100_plus_width_times_510_plus_height_times_480,
    xcf_file_size_times_83_plus_image_type_times_5600_plus_width_times_height_times_2400,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 606190
FN2_EXPECTED = 17174


class TestXcfFileSizeMod257Times3400PlusImageTypeTimes5100PlusWidthTimes510PlusHeightTimes480:
    def test_returns_int(self):
        result = xcf_file_size_mod_257_times_3400_plus_image_type_times_5100_plus_width_times_510_plus_height_times_480(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_257_times_3400_plus_image_type_times_5100_plus_width_times_510_plus_height_times_480(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_257_times_3400_plus_image_type_times_5100_plus_width_times_510_plus_height_times_480(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_257_times_3400_plus_image_type_times_5100_plus_width_times_510_plus_height_times_480(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_257_times_3400_plus_image_type_times_5100_plus_width_times_510_plus_height_times_480(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes83PlusImageTypeTimes5600PlusWidthTimesHeightTimes2400:
    def test_returns_int(self):
        result = xcf_file_size_times_83_plus_image_type_times_5600_plus_width_times_height_times_2400(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_83_plus_image_type_times_5600_plus_width_times_height_times_2400(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_83_plus_image_type_times_5600_plus_width_times_height_times_2400(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_83_plus_image_type_times_5600_plus_width_times_height_times_2400(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_83_plus_image_type_times_5600_plus_width_times_height_times_2400(_SAMPLE)
        assert result == FN2_EXPECTED
