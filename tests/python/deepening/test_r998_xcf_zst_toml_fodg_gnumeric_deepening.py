"""Sprint 445 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_353_times_235_plus_shape_times_14800_plus_text_times_14400_plus_page_times_12700,
    fodg_file_size_times_129_plus_shape_times_54_plus_text_times_53_plus_page_times_54,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 94245
FN2_EXPECTED = 135891


class TestFodgFileSizeMod353Times235PlusShapeTimes14800PlusTextTimes14400PlusPageTimes12700:
    def test_returns_int(self):
        result = fodg_file_size_mod_353_times_235_plus_shape_times_14800_plus_text_times_14400_plus_page_times_12700(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_353_times_235_plus_shape_times_14800_plus_text_times_14400_plus_page_times_12700(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_353_times_235_plus_shape_times_14800_plus_text_times_14400_plus_page_times_12700(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_353_times_235_plus_shape_times_14800_plus_text_times_14400_plus_page_times_12700(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_353_times_235_plus_shape_times_14800_plus_text_times_14400_plus_page_times_12700(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes129PlusShapeTimes54PlusTextTimes53PlusPageTimes54:
    def test_returns_int(self):
        result = fodg_file_size_times_129_plus_shape_times_54_plus_text_times_53_plus_page_times_54(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_129_plus_shape_times_54_plus_text_times_53_plus_page_times_54(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_129_plus_shape_times_54_plus_text_times_53_plus_page_times_54(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_129_plus_shape_times_54_plus_text_times_53_plus_page_times_54(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_129_plus_shape_times_54_plus_text_times_53_plus_page_times_54(_SAMPLE)
        assert result == FN2_EXPECTED
