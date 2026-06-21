"""Sprint 517 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_521_times_365_plus_shape_times_19600_plus_text_times_19200_plus_page_times_17500,
    fodg_file_size_times_177_plus_shape_times_78_plus_text_times_77_plus_page_times_78,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 21515
FN2_EXPECTED = 186459


class TestFodgFileSizeMod521Times365PlusShapeTimes19600PlusTextTimes19200PlusPageTimes17500:
    def test_returns_int(self):
        result = fodg_file_size_mod_521_times_365_plus_shape_times_19600_plus_text_times_19200_plus_page_times_17500(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_521_times_365_plus_shape_times_19600_plus_text_times_19200_plus_page_times_17500(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_521_times_365_plus_shape_times_19600_plus_text_times_19200_plus_page_times_17500(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_521_times_365_plus_shape_times_19600_plus_text_times_19200_plus_page_times_17500(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_521_times_365_plus_shape_times_19600_plus_text_times_19200_plus_page_times_17500(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes177PlusShapeTimes78PlusTextTimes77PlusPageTimes78:
    def test_returns_int(self):
        result = fodg_file_size_times_177_plus_shape_times_78_plus_text_times_77_plus_page_times_78(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_177_plus_shape_times_78_plus_text_times_77_plus_page_times_78(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_177_plus_shape_times_78_plus_text_times_77_plus_page_times_78(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_177_plus_shape_times_78_plus_text_times_77_plus_page_times_78(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_177_plus_shape_times_78_plus_text_times_77_plus_page_times_78(_SAMPLE)
        assert result == FN2_EXPECTED
