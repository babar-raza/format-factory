"""Sprint 505 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_479_times_345_plus_shape_times_18800_plus_text_times_18400_plus_page_times_16700,
    fodg_file_size_times_169_plus_shape_times_74_plus_text_times_73_plus_page_times_74,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 49475
FN2_EXPECTED = 178031


class TestFodgFileSizeMod479Times345PlusShapeTimes18800PlusTextTimes18400PlusPageTimes16700:
    def test_returns_int(self):
        result = fodg_file_size_mod_479_times_345_plus_shape_times_18800_plus_text_times_18400_plus_page_times_16700(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_479_times_345_plus_shape_times_18800_plus_text_times_18400_plus_page_times_16700(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_479_times_345_plus_shape_times_18800_plus_text_times_18400_plus_page_times_16700(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_479_times_345_plus_shape_times_18800_plus_text_times_18400_plus_page_times_16700(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_479_times_345_plus_shape_times_18800_plus_text_times_18400_plus_page_times_16700(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes169PlusShapeTimes74PlusTextTimes73PlusPageTimes74:
    def test_returns_int(self):
        result = fodg_file_size_times_169_plus_shape_times_74_plus_text_times_73_plus_page_times_74(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_169_plus_shape_times_74_plus_text_times_73_plus_page_times_74(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_169_plus_shape_times_74_plus_text_times_73_plus_page_times_74(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_169_plus_shape_times_74_plus_text_times_73_plus_page_times_74(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_169_plus_shape_times_74_plus_text_times_73_plus_page_times_74(_SAMPLE)
        assert result == FN2_EXPECTED
