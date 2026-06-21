"""Sprint 436 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_333_times_220_plus_shape_times_14200_plus_text_times_13800_plus_page_times_12100,
    fodg_file_size_times_123_plus_shape_times_51_plus_text_times_50_plus_page_times_51,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 23980
FN2_EXPECTED = 129570


class TestFodgFileSizeMod333Times220PlusShapeTimes14200PlusTextTimes13800PlusPageTimes12100:
    def test_returns_int(self):
        result = fodg_file_size_mod_333_times_220_plus_shape_times_14200_plus_text_times_13800_plus_page_times_12100(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_333_times_220_plus_shape_times_14200_plus_text_times_13800_plus_page_times_12100(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_333_times_220_plus_shape_times_14200_plus_text_times_13800_plus_page_times_12100(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_333_times_220_plus_shape_times_14200_plus_text_times_13800_plus_page_times_12100(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_333_times_220_plus_shape_times_14200_plus_text_times_13800_plus_page_times_12100(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes123PlusShapeTimes51PlusTextTimes50PlusPageTimes51:
    def test_returns_int(self):
        result = fodg_file_size_times_123_plus_shape_times_51_plus_text_times_50_plus_page_times_51(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_123_plus_shape_times_51_plus_text_times_50_plus_page_times_51(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_123_plus_shape_times_51_plus_text_times_50_plus_page_times_51(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_123_plus_shape_times_51_plus_text_times_50_plus_page_times_51(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_123_plus_shape_times_51_plus_text_times_50_plus_page_times_51(_SAMPLE)
        assert result == FN2_EXPECTED
