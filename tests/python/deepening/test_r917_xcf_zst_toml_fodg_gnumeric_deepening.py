"""Sprint 364 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_231_times_100_plus_shape_times_9400_plus_text_times_9000_plus_page_times_7300,
    fodg_file_size_times_67_plus_shape_times_27_plus_text_times_26_plus_page_times_27,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 20200
FN2_EXPECTED = 70578


class TestFodgFileSizeMod231Times100PlusShapeTimes9400PlusTextTimes9000PlusPageTimes7300:
    def test_returns_int(self):
        result = fodg_file_size_mod_231_times_100_plus_shape_times_9400_plus_text_times_9000_plus_page_times_7300(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_231_times_100_plus_shape_times_9400_plus_text_times_9000_plus_page_times_7300(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_231_times_100_plus_shape_times_9400_plus_text_times_9000_plus_page_times_7300(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_231_times_100_plus_shape_times_9400_plus_text_times_9000_plus_page_times_7300(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_231_times_100_plus_shape_times_9400_plus_text_times_9000_plus_page_times_7300(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes67PlusShapeTimes27PlusTextTimes26PlusPageTimes27:
    def test_returns_int(self):
        result = fodg_file_size_times_67_plus_shape_times_27_plus_text_times_26_plus_page_times_27(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_67_plus_shape_times_27_plus_text_times_26_plus_page_times_27(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_67_plus_shape_times_27_plus_text_times_26_plus_page_times_27(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_67_plus_shape_times_27_plus_text_times_26_plus_page_times_27(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_67_plus_shape_times_27_plus_text_times_26_plus_page_times_27(_SAMPLE)
        assert result == FN2_EXPECTED
