"""Sprint 370 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_241_times_110_plus_shape_times_9800_plus_text_times_9400_plus_page_times_7700,
    fodg_file_size_times_71_plus_shape_times_29_plus_text_times_28_plus_page_times_29,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 17490
FN2_EXPECTED = 74792


class TestFodgFileSizeMod241Times110PlusShapeTimes9800PlusTextTimes9400PlusPageTimes7700:
    def test_returns_int(self):
        result = fodg_file_size_mod_241_times_110_plus_shape_times_9800_plus_text_times_9400_plus_page_times_7700(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_241_times_110_plus_shape_times_9800_plus_text_times_9400_plus_page_times_7700(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_241_times_110_plus_shape_times_9800_plus_text_times_9400_plus_page_times_7700(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_241_times_110_plus_shape_times_9800_plus_text_times_9400_plus_page_times_7700(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_241_times_110_plus_shape_times_9800_plus_text_times_9400_plus_page_times_7700(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes71PlusShapeTimes29PlusTextTimes28PlusPageTimes29:
    def test_returns_int(self):
        result = fodg_file_size_times_71_plus_shape_times_29_plus_text_times_28_plus_page_times_29(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_71_plus_shape_times_29_plus_text_times_28_plus_page_times_29(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_71_plus_shape_times_29_plus_text_times_28_plus_page_times_29(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_71_plus_shape_times_29_plus_text_times_28_plus_page_times_29(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_71_plus_shape_times_29_plus_text_times_28_plus_page_times_29(_SAMPLE)
        assert result == FN2_EXPECTED
