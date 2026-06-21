"""Sprint 520 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_523_times_367_plus_shape_times_19800_plus_text_times_19400_plus_page_times_17700,
    fodg_file_size_times_181_plus_shape_times_80_plus_text_times_79_plus_page_times_80,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 20269
FN2_EXPECTED = 190673


class TestFodgFileSizeMod523Times367PlusShapeTimes19800PlusTextTimes19400PlusPageTimes17700:
    def test_returns_int(self):
        result = fodg_file_size_mod_523_times_367_plus_shape_times_19800_plus_text_times_19400_plus_page_times_17700(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_523_times_367_plus_shape_times_19800_plus_text_times_19400_plus_page_times_17700(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_523_times_367_plus_shape_times_19800_plus_text_times_19400_plus_page_times_17700(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_523_times_367_plus_shape_times_19800_plus_text_times_19400_plus_page_times_17700(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_523_times_367_plus_shape_times_19800_plus_text_times_19400_plus_page_times_17700(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes181PlusShapeTimes80PlusTextTimes79PlusPageTimes80:
    def test_returns_int(self):
        result = fodg_file_size_times_181_plus_shape_times_80_plus_text_times_79_plus_page_times_80(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_181_plus_shape_times_80_plus_text_times_79_plus_page_times_80(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_181_plus_shape_times_80_plus_text_times_79_plus_page_times_80(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_181_plus_shape_times_80_plus_text_times_79_plus_page_times_80(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_181_plus_shape_times_80_plus_text_times_79_plus_page_times_80(_SAMPLE)
        assert result == FN2_EXPECTED
