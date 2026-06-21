"""Sprint 376 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_251_times_120_plus_shape_times_10200_plus_text_times_9800_plus_page_times_8100,
    fodg_file_size_times_79_plus_shape_times_31_plus_text_times_30_plus_page_times_31,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 13980
FN2_EXPECTED = 83218


class TestFodgFileSizeMod251Times120PlusShapeTimes10200PlusTextTimes9800PlusPageTimes8100:
    def test_returns_int(self):
        result = fodg_file_size_mod_251_times_120_plus_shape_times_10200_plus_text_times_9800_plus_page_times_8100(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_251_times_120_plus_shape_times_10200_plus_text_times_9800_plus_page_times_8100(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_251_times_120_plus_shape_times_10200_plus_text_times_9800_plus_page_times_8100(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_251_times_120_plus_shape_times_10200_plus_text_times_9800_plus_page_times_8100(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_251_times_120_plus_shape_times_10200_plus_text_times_9800_plus_page_times_8100(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes79PlusShapeTimes31PlusTextTimes30PlusPageTimes31:
    def test_returns_int(self):
        result = fodg_file_size_times_79_plus_shape_times_31_plus_text_times_30_plus_page_times_31(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_79_plus_shape_times_31_plus_text_times_30_plus_page_times_31(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_79_plus_shape_times_31_plus_text_times_30_plus_page_times_31(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_79_plus_shape_times_31_plus_text_times_30_plus_page_times_31(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_79_plus_shape_times_31_plus_text_times_30_plus_page_times_31(_SAMPLE)
        assert result == FN2_EXPECTED
