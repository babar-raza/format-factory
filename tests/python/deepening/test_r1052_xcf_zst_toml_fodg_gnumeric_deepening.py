"""Sprint 499 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_463_times_335_plus_shape_times_18400_plus_text_times_18000_plus_page_times_16300,
    fodg_file_size_times_165_plus_shape_times_72_plus_text_times_71_plus_page_times_72,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 58845
FN2_EXPECTED = 173817


class TestFodgFileSizeMod463Times335PlusShapeTimes18400PlusTextTimes18000PlusPageTimes16300:
    def test_returns_int(self):
        result = fodg_file_size_mod_463_times_335_plus_shape_times_18400_plus_text_times_18000_plus_page_times_16300(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_463_times_335_plus_shape_times_18400_plus_text_times_18000_plus_page_times_16300(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_463_times_335_plus_shape_times_18400_plus_text_times_18000_plus_page_times_16300(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_463_times_335_plus_shape_times_18400_plus_text_times_18000_plus_page_times_16300(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_463_times_335_plus_shape_times_18400_plus_text_times_18000_plus_page_times_16300(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes165PlusShapeTimes72PlusTextTimes71PlusPageTimes72:
    def test_returns_int(self):
        result = fodg_file_size_times_165_plus_shape_times_72_plus_text_times_71_plus_page_times_72(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_165_plus_shape_times_72_plus_text_times_71_plus_page_times_72(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_165_plus_shape_times_72_plus_text_times_71_plus_page_times_72(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_165_plus_shape_times_72_plus_text_times_71_plus_page_times_72(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_165_plus_shape_times_72_plus_text_times_71_plus_page_times_72(_SAMPLE)
        assert result == FN2_EXPECTED
