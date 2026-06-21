"""Sprint 508 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_487_times_350_plus_shape_times_19000_plus_text_times_18600_plus_page_times_16900,
    fodg_file_size_times_171_plus_shape_times_75_plus_text_times_74_plus_page_times_75,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 44550
FN2_EXPECTED = 180138


class TestFodgFileSizeMod487Times350PlusShapeTimes19000PlusTextTimes18600PlusPageTimes16900:
    def test_returns_int(self):
        result = fodg_file_size_mod_487_times_350_plus_shape_times_19000_plus_text_times_18600_plus_page_times_16900(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_487_times_350_plus_shape_times_19000_plus_text_times_18600_plus_page_times_16900(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_487_times_350_plus_shape_times_19000_plus_text_times_18600_plus_page_times_16900(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_487_times_350_plus_shape_times_19000_plus_text_times_18600_plus_page_times_16900(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_487_times_350_plus_shape_times_19000_plus_text_times_18600_plus_page_times_16900(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes171PlusShapeTimes75PlusTextTimes74PlusPageTimes75:
    def test_returns_int(self):
        result = fodg_file_size_times_171_plus_shape_times_75_plus_text_times_74_plus_page_times_75(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_171_plus_shape_times_75_plus_text_times_74_plus_page_times_75(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_171_plus_shape_times_75_plus_text_times_74_plus_page_times_75(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_171_plus_shape_times_75_plus_text_times_74_plus_page_times_75(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_171_plus_shape_times_75_plus_text_times_74_plus_page_times_75(_SAMPLE)
        assert result == FN2_EXPECTED
