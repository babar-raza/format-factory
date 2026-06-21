"""Sprint 406 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_301_times_170_plus_shape_times_12200_plus_text_times_11800_plus_page_times_10100,
    fodg_file_size_times_99_plus_shape_times_40_plus_text_times_39_plus_page_times_40,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 35600
FN2_EXPECTED = 104287


class TestFodgFileSizeMod301Times170PlusShapeTimes12200PlusTextTimes11800PlusPageTimes10100:
    def test_returns_int(self):
        result = fodg_file_size_mod_301_times_170_plus_shape_times_12200_plus_text_times_11800_plus_page_times_10100(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_301_times_170_plus_shape_times_12200_plus_text_times_11800_plus_page_times_10100(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_301_times_170_plus_shape_times_12200_plus_text_times_11800_plus_page_times_10100(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_301_times_170_plus_shape_times_12200_plus_text_times_11800_plus_page_times_10100(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_301_times_170_plus_shape_times_12200_plus_text_times_11800_plus_page_times_10100(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes99PlusShapeTimes40PlusTextTimes39PlusPageTimes40:
    def test_returns_int(self):
        result = fodg_file_size_times_99_plus_shape_times_40_plus_text_times_39_plus_page_times_40(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_99_plus_shape_times_40_plus_text_times_39_plus_page_times_40(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_99_plus_shape_times_40_plus_text_times_39_plus_page_times_40(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_99_plus_shape_times_40_plus_text_times_39_plus_page_times_40(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_99_plus_shape_times_40_plus_text_times_39_plus_page_times_40(_SAMPLE)
        assert result == FN2_EXPECTED
