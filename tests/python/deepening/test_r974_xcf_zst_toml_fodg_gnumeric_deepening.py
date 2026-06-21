"""Sprint 421 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_321_times_195_plus_shape_times_13200_plus_text_times_12800_plus_page_times_11100,
    fodg_file_size_times_109_plus_shape_times_45_plus_text_times_44_plus_page_times_45,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 28650
FN2_EXPECTED = 114822


class TestFodgFileSizeMod321Times195PlusShapeTimes13200PlusTextTimes12800PlusPageTimes11100:
    def test_returns_int(self):
        result = fodg_file_size_mod_321_times_195_plus_shape_times_13200_plus_text_times_12800_plus_page_times_11100(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_321_times_195_plus_shape_times_13200_plus_text_times_12800_plus_page_times_11100(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_321_times_195_plus_shape_times_13200_plus_text_times_12800_plus_page_times_11100(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_321_times_195_plus_shape_times_13200_plus_text_times_12800_plus_page_times_11100(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_321_times_195_plus_shape_times_13200_plus_text_times_12800_plus_page_times_11100(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes109PlusShapeTimes45PlusTextTimes44PlusPageTimes45:
    def test_returns_int(self):
        result = fodg_file_size_times_109_plus_shape_times_45_plus_text_times_44_plus_page_times_45(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_109_plus_shape_times_45_plus_text_times_44_plus_page_times_45(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_109_plus_shape_times_45_plus_text_times_44_plus_page_times_45(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_109_plus_shape_times_45_plus_text_times_44_plus_page_times_45(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_109_plus_shape_times_45_plus_text_times_44_plus_page_times_45(_SAMPLE)
        assert result == FN2_EXPECTED
