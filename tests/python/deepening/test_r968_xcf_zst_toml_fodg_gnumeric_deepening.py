"""Sprint 415 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_309_times_185_plus_shape_times_12800_plus_text_times_12400_plus_page_times_10700,
    fodg_file_size_times_105_plus_shape_times_43_plus_text_times_42_plus_page_times_43,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 34010
FN2_EXPECTED = 110608


class TestFodgFileSizeMod309Times185PlusShapeTimes12800PlusTextTimes12400PlusPageTimes10700:
    def test_returns_int(self):
        result = fodg_file_size_mod_309_times_185_plus_shape_times_12800_plus_text_times_12400_plus_page_times_10700(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_309_times_185_plus_shape_times_12800_plus_text_times_12400_plus_page_times_10700(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_309_times_185_plus_shape_times_12800_plus_text_times_12400_plus_page_times_10700(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_309_times_185_plus_shape_times_12800_plus_text_times_12400_plus_page_times_10700(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_309_times_185_plus_shape_times_12800_plus_text_times_12400_plus_page_times_10700(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes105PlusShapeTimes43PlusTextTimes42PlusPageTimes43:
    def test_returns_int(self):
        result = fodg_file_size_times_105_plus_shape_times_43_plus_text_times_42_plus_page_times_43(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_105_plus_shape_times_43_plus_text_times_42_plus_page_times_43(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_105_plus_shape_times_43_plus_text_times_42_plus_page_times_43(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_105_plus_shape_times_43_plus_text_times_42_plus_page_times_43(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_105_plus_shape_times_43_plus_text_times_42_plus_page_times_43(_SAMPLE)
        assert result == FN2_EXPECTED
