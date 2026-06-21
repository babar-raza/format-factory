"""Sprint 493 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_449_times_320_plus_shape_times_18000_plus_text_times_17600_plus_page_times_15900,
    fodg_file_size_times_161_plus_shape_times_70_plus_text_times_69_plus_page_times_70,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 65500
FN2_EXPECTED = 169603


class TestFodgFileSizeMod449Times320PlusShapeTimes18000PlusTextTimes17600PlusPageTimes15900:
    def test_returns_int(self):
        result = fodg_file_size_mod_449_times_320_plus_shape_times_18000_plus_text_times_17600_plus_page_times_15900(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_449_times_320_plus_shape_times_18000_plus_text_times_17600_plus_page_times_15900(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_449_times_320_plus_shape_times_18000_plus_text_times_17600_plus_page_times_15900(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_449_times_320_plus_shape_times_18000_plus_text_times_17600_plus_page_times_15900(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_449_times_320_plus_shape_times_18000_plus_text_times_17600_plus_page_times_15900(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes161PlusShapeTimes70PlusTextTimes69PlusPageTimes70:
    def test_returns_int(self):
        result = fodg_file_size_times_161_plus_shape_times_70_plus_text_times_69_plus_page_times_70(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_161_plus_shape_times_70_plus_text_times_69_plus_page_times_70(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_161_plus_shape_times_70_plus_text_times_69_plus_page_times_70(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_161_plus_shape_times_70_plus_text_times_69_plus_page_times_70(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_161_plus_shape_times_70_plus_text_times_69_plus_page_times_70(_SAMPLE)
        assert result == FN2_EXPECTED
