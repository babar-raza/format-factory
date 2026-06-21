"""Sprint 394 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_277_times_150_plus_shape_times_11400_plus_text_times_11000_plus_page_times_9300,
    fodg_file_size_times_91_plus_shape_times_36_plus_text_times_35_plus_page_times_36,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 42600
FN2_EXPECTED = 95859


class TestFodgFileSizeMod277Times150PlusShapeTimes11400PlusTextTimes11000PlusPageTimes9300:
    def test_returns_int(self):
        result = fodg_file_size_mod_277_times_150_plus_shape_times_11400_plus_text_times_11000_plus_page_times_9300(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_277_times_150_plus_shape_times_11400_plus_text_times_11000_plus_page_times_9300(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_277_times_150_plus_shape_times_11400_plus_text_times_11000_plus_page_times_9300(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_277_times_150_plus_shape_times_11400_plus_text_times_11000_plus_page_times_9300(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_277_times_150_plus_shape_times_11400_plus_text_times_11000_plus_page_times_9300(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes91PlusShapeTimes36PlusTextTimes35PlusPageTimes36:
    def test_returns_int(self):
        result = fodg_file_size_times_91_plus_shape_times_36_plus_text_times_35_plus_page_times_36(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_91_plus_shape_times_36_plus_text_times_35_plus_page_times_36(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_91_plus_shape_times_36_plus_text_times_35_plus_page_times_36(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_91_plus_shape_times_36_plus_text_times_35_plus_page_times_36(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_91_plus_shape_times_36_plus_text_times_35_plus_page_times_36(_SAMPLE)
        assert result == FN2_EXPECTED
