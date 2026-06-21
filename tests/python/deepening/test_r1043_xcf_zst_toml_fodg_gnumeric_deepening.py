"""Sprint 490 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_443_times_315_plus_shape_times_17800_plus_text_times_17400_plus_page_times_15700,
    fodg_file_size_times_159_plus_shape_times_69_plus_text_times_68_plus_page_times_69,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 68305
FN2_EXPECTED = 167496


class TestFodgFileSizeMod443Times315PlusShapeTimes17800PlusTextTimes17400PlusPageTimes15700:
    def test_returns_int(self):
        result = fodg_file_size_mod_443_times_315_plus_shape_times_17800_plus_text_times_17400_plus_page_times_15700(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_443_times_315_plus_shape_times_17800_plus_text_times_17400_plus_page_times_15700(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_443_times_315_plus_shape_times_17800_plus_text_times_17400_plus_page_times_15700(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_443_times_315_plus_shape_times_17800_plus_text_times_17400_plus_page_times_15700(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_443_times_315_plus_shape_times_17800_plus_text_times_17400_plus_page_times_15700(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes159PlusShapeTimes69PlusTextTimes68PlusPageTimes69:
    def test_returns_int(self):
        result = fodg_file_size_times_159_plus_shape_times_69_plus_text_times_68_plus_page_times_69(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_159_plus_shape_times_69_plus_text_times_68_plus_page_times_69(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_159_plus_shape_times_69_plus_text_times_68_plus_page_times_69(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_159_plus_shape_times_69_plus_text_times_68_plus_page_times_69(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_159_plus_shape_times_69_plus_text_times_68_plus_page_times_69(_SAMPLE)
        assert result == FN2_EXPECTED
