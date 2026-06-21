"""Sprint 498 - XCF deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_439_times_7300_plus_image_type_times_9300_plus_width_times_920_plus_height_times_890,
    xcf_file_size_times_171_plus_image_type_times_11300_plus_width_times_height_times_6400,
)

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-rgba-blue.xcf"

FN1_EXPECTED = 1301210
FN2_EXPECTED = 36838


class TestXcfFileSizeMod439Times7300PlusImageTypeTimes9300PlusWidthTimes920PlusHeightTimes890:
    def test_returns_int(self):
        result = xcf_file_size_mod_439_times_7300_plus_image_type_times_9300_plus_width_times_920_plus_height_times_890(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_mod_439_times_7300_plus_image_type_times_9300_plus_width_times_920_plus_height_times_890(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = xcf_file_size_mod_439_times_7300_plus_image_type_times_9300_plus_width_times_920_plus_height_times_890(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_mod_439_times_7300_plus_image_type_times_9300_plus_width_times_920_plus_height_times_890(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_439_times_7300_plus_image_type_times_9300_plus_width_times_920_plus_height_times_890(_SAMPLE)
        assert result == FN1_EXPECTED


class TestXcfFileSizeTimes171PlusImageTypeTimes11300PlusWidthTimesHeightTimes6400:
    def test_returns_int(self):
        result = xcf_file_size_times_171_plus_image_type_times_11300_plus_width_times_height_times_6400(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = xcf_file_size_times_171_plus_image_type_times_11300_plus_width_times_height_times_6400(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = xcf_file_size_times_171_plus_image_type_times_11300_plus_width_times_height_times_6400(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = xcf_file_size_times_171_plus_image_type_times_11300_plus_width_times_height_times_6400(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = xcf_file_size_times_171_plus_image_type_times_11300_plus_width_times_height_times_6400(_SAMPLE)
        assert result == FN2_EXPECTED
