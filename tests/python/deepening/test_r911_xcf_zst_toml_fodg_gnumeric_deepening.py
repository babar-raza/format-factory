"""Sprint 358 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_221_times_90_plus_shape_times_9000_plus_text_times_8600_plus_page_times_6900,
    fodg_file_size_times_63_plus_shape_times_25_plus_text_times_24_plus_page_times_25,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 22110
FN2_EXPECTED = 66364


class TestFodgFileSizeMod221Times90PlusShapeTimes9000PlusTextTimes8600PlusPageTimes6900:
    def test_returns_int(self):
        result = fodg_file_size_mod_221_times_90_plus_shape_times_9000_plus_text_times_8600_plus_page_times_6900(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_221_times_90_plus_shape_times_9000_plus_text_times_8600_plus_page_times_6900(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_221_times_90_plus_shape_times_9000_plus_text_times_8600_plus_page_times_6900(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_221_times_90_plus_shape_times_9000_plus_text_times_8600_plus_page_times_6900(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_221_times_90_plus_shape_times_9000_plus_text_times_8600_plus_page_times_6900(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes63PlusShapeTimes25PlusTextTimes24PlusPageTimes25:
    def test_returns_int(self):
        result = fodg_file_size_times_63_plus_shape_times_25_plus_text_times_24_plus_page_times_25(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_63_plus_shape_times_25_plus_text_times_24_plus_page_times_25(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_63_plus_shape_times_25_plus_text_times_24_plus_page_times_25(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_63_plus_shape_times_25_plus_text_times_24_plus_page_times_25(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_63_plus_shape_times_25_plus_text_times_24_plus_page_times_25(_SAMPLE)
        assert result == FN2_EXPECTED
