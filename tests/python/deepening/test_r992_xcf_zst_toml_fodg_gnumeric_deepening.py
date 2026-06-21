"""Sprint 439 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_339_times_225_plus_shape_times_14400_plus_text_times_14000_plus_page_times_12300,
    fodg_file_size_times_125_plus_shape_times_52_plus_text_times_51_plus_page_times_52,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 20400
FN2_EXPECTED = 131677


class TestFodgFileSizeMod339Times225PlusShapeTimes14400PlusTextTimes14000PlusPageTimes12300:
    def test_returns_int(self):
        result = fodg_file_size_mod_339_times_225_plus_shape_times_14400_plus_text_times_14000_plus_page_times_12300(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_339_times_225_plus_shape_times_14400_plus_text_times_14000_plus_page_times_12300(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_339_times_225_plus_shape_times_14400_plus_text_times_14000_plus_page_times_12300(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_339_times_225_plus_shape_times_14400_plus_text_times_14000_plus_page_times_12300(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_339_times_225_plus_shape_times_14400_plus_text_times_14000_plus_page_times_12300(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes125PlusShapeTimes52PlusTextTimes51PlusPageTimes52:
    def test_returns_int(self):
        result = fodg_file_size_times_125_plus_shape_times_52_plus_text_times_51_plus_page_times_52(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_125_plus_shape_times_52_plus_text_times_51_plus_page_times_52(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_125_plus_shape_times_52_plus_text_times_51_plus_page_times_52(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_125_plus_shape_times_52_plus_text_times_51_plus_page_times_52(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_125_plus_shape_times_52_plus_text_times_51_plus_page_times_52(_SAMPLE)
        assert result == FN2_EXPECTED
