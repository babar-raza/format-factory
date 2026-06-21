"""Sprint 391 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_271_times_145_plus_shape_times_11200_plus_text_times_10800_plus_page_times_9100,
    fodg_file_size_times_89_plus_shape_times_35_plus_text_times_34_plus_page_times_35,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 43900
FN2_EXPECTED = 93752


class TestFodgFileSizeMod271Times145PlusShapeTimes11200PlusTextTimes10800PlusPageTimes9100:
    def test_returns_int(self):
        result = fodg_file_size_mod_271_times_145_plus_shape_times_11200_plus_text_times_10800_plus_page_times_9100(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_271_times_145_plus_shape_times_11200_plus_text_times_10800_plus_page_times_9100(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_271_times_145_plus_shape_times_11200_plus_text_times_10800_plus_page_times_9100(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_271_times_145_plus_shape_times_11200_plus_text_times_10800_plus_page_times_9100(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_271_times_145_plus_shape_times_11200_plus_text_times_10800_plus_page_times_9100(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes89PlusShapeTimes35PlusTextTimes34PlusPageTimes35:
    def test_returns_int(self):
        result = fodg_file_size_times_89_plus_shape_times_35_plus_text_times_34_plus_page_times_35(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_89_plus_shape_times_35_plus_text_times_34_plus_page_times_35(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_89_plus_shape_times_35_plus_text_times_34_plus_page_times_35(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_89_plus_shape_times_35_plus_text_times_34_plus_page_times_35(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_89_plus_shape_times_35_plus_text_times_34_plus_page_times_35(_SAMPLE)
        assert result == FN2_EXPECTED
