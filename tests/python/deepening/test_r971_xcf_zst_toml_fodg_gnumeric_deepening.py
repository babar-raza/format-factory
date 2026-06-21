"""Sprint 418 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_319_times_190_plus_shape_times_13000_plus_text_times_12600_plus_page_times_10900,
    fodg_file_size_times_107_plus_shape_times_44_plus_text_times_43_plus_page_times_44,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 29140
FN2_EXPECTED = 112715


class TestFodgFileSizeMod319Times190PlusShapeTimes13000PlusTextTimes12600PlusPageTimes10900:
    def test_returns_int(self):
        result = fodg_file_size_mod_319_times_190_plus_shape_times_13000_plus_text_times_12600_plus_page_times_10900(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_319_times_190_plus_shape_times_13000_plus_text_times_12600_plus_page_times_10900(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_319_times_190_plus_shape_times_13000_plus_text_times_12600_plus_page_times_10900(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_319_times_190_plus_shape_times_13000_plus_text_times_12600_plus_page_times_10900(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_319_times_190_plus_shape_times_13000_plus_text_times_12600_plus_page_times_10900(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes107PlusShapeTimes44PlusTextTimes43PlusPageTimes44:
    def test_returns_int(self):
        result = fodg_file_size_times_107_plus_shape_times_44_plus_text_times_43_plus_page_times_44(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_107_plus_shape_times_44_plus_text_times_43_plus_page_times_44(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_107_plus_shape_times_44_plus_text_times_43_plus_page_times_44(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_107_plus_shape_times_44_plus_text_times_43_plus_page_times_44(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_107_plus_shape_times_44_plus_text_times_43_plus_page_times_44(_SAMPLE)
        assert result == FN2_EXPECTED
