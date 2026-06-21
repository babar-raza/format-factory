"""Sprint 367 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_235_times_105_plus_shape_times_9600_plus_text_times_9200_plus_page_times_7500,
    fodg_file_size_times_69_plus_shape_times_28_plus_text_times_27_plus_page_times_28,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 19365
FN2_EXPECTED = 72685


class TestFodgFileSizeMod235Times105PlusShapeTimes9600PlusTextTimes9200PlusPageTimes7500:
    def test_returns_int(self):
        result = fodg_file_size_mod_235_times_105_plus_shape_times_9600_plus_text_times_9200_plus_page_times_7500(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_235_times_105_plus_shape_times_9600_plus_text_times_9200_plus_page_times_7500(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_235_times_105_plus_shape_times_9600_plus_text_times_9200_plus_page_times_7500(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_235_times_105_plus_shape_times_9600_plus_text_times_9200_plus_page_times_7500(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_235_times_105_plus_shape_times_9600_plus_text_times_9200_plus_page_times_7500(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes69PlusShapeTimes28PlusTextTimes27PlusPageTimes28:
    def test_returns_int(self):
        result = fodg_file_size_times_69_plus_shape_times_28_plus_text_times_27_plus_page_times_28(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_69_plus_shape_times_28_plus_text_times_27_plus_page_times_28(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_69_plus_shape_times_28_plus_text_times_27_plus_page_times_28(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_69_plus_shape_times_28_plus_text_times_27_plus_page_times_28(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_69_plus_shape_times_28_plus_text_times_27_plus_page_times_28(_SAMPLE)
        assert result == FN2_EXPECTED
