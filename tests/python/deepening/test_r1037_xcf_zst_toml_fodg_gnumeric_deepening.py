"""Sprint 484 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_423_times_300_plus_shape_times_17400_plus_text_times_17000_plus_page_times_15300,
    fodg_file_size_times_155_plus_shape_times_67_plus_text_times_66_plus_page_times_67,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 77400
FN2_EXPECTED = 163282


class TestFodgFileSizeMod423Times300PlusShapeTimes17400PlusTextTimes17000PlusPageTimes15300:
    def test_returns_int(self):
        result = fodg_file_size_mod_423_times_300_plus_shape_times_17400_plus_text_times_17000_plus_page_times_15300(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_423_times_300_plus_shape_times_17400_plus_text_times_17000_plus_page_times_15300(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_423_times_300_plus_shape_times_17400_plus_text_times_17000_plus_page_times_15300(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_423_times_300_plus_shape_times_17400_plus_text_times_17000_plus_page_times_15300(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_423_times_300_plus_shape_times_17400_plus_text_times_17000_plus_page_times_15300(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes155PlusShapeTimes67PlusTextTimes66PlusPageTimes67:
    def test_returns_int(self):
        result = fodg_file_size_times_155_plus_shape_times_67_plus_text_times_66_plus_page_times_67(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_155_plus_shape_times_67_plus_text_times_66_plus_page_times_67(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_155_plus_shape_times_67_plus_text_times_66_plus_page_times_67(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_155_plus_shape_times_67_plus_text_times_66_plus_page_times_67(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_155_plus_shape_times_67_plus_text_times_66_plus_page_times_67(_SAMPLE)
        assert result == FN2_EXPECTED
