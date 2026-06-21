"""Sprint 481 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_421_times_295_plus_shape_times_17200_plus_text_times_16800_plus_page_times_15100,
    fodg_file_size_times_153_plus_shape_times_66_plus_text_times_65_plus_page_times_66,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 77345
FN2_EXPECTED = 161175


class TestFodgFileSizeMod421Times295PlusShapeTimes17200PlusTextTimes16800PlusPageTimes15100:
    def test_returns_int(self):
        result = fodg_file_size_mod_421_times_295_plus_shape_times_17200_plus_text_times_16800_plus_page_times_15100(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_421_times_295_plus_shape_times_17200_plus_text_times_16800_plus_page_times_15100(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_421_times_295_plus_shape_times_17200_plus_text_times_16800_plus_page_times_15100(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_421_times_295_plus_shape_times_17200_plus_text_times_16800_plus_page_times_15100(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_421_times_295_plus_shape_times_17200_plus_text_times_16800_plus_page_times_15100(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes153PlusShapeTimes66PlusTextTimes65PlusPageTimes66:
    def test_returns_int(self):
        result = fodg_file_size_times_153_plus_shape_times_66_plus_text_times_65_plus_page_times_66(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_153_plus_shape_times_66_plus_text_times_65_plus_page_times_66(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_153_plus_shape_times_66_plus_text_times_65_plus_page_times_66(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_153_plus_shape_times_66_plus_text_times_65_plus_page_times_66(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_153_plus_shape_times_66_plus_text_times_65_plus_page_times_66(_SAMPLE)
        assert result == FN2_EXPECTED
