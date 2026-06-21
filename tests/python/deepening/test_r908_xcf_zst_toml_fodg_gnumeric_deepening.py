"""Sprint 355 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_219_times_85_plus_shape_times_8800_plus_text_times_8400_plus_page_times_6700,
    fodg_file_size_times_59_plus_shape_times_24_plus_text_times_23_plus_page_times_24,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 21745
FN2_EXPECTED = 62151


class TestFodgFileSizeMod219Times85PlusShapeTimes8800PlusTextTimes8400PlusPageTimes6700:
    def test_returns_int(self):
        result = fodg_file_size_mod_219_times_85_plus_shape_times_8800_plus_text_times_8400_plus_page_times_6700(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_219_times_85_plus_shape_times_8800_plus_text_times_8400_plus_page_times_6700(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_219_times_85_plus_shape_times_8800_plus_text_times_8400_plus_page_times_6700(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_219_times_85_plus_shape_times_8800_plus_text_times_8400_plus_page_times_6700(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_219_times_85_plus_shape_times_8800_plus_text_times_8400_plus_page_times_6700(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes59PlusShapeTimes24PlusTextTimes23PlusPageTimes24:
    def test_returns_int(self):
        result = fodg_file_size_times_59_plus_shape_times_24_plus_text_times_23_plus_page_times_24(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_59_plus_shape_times_24_plus_text_times_23_plus_page_times_24(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_59_plus_shape_times_24_plus_text_times_23_plus_page_times_24(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_59_plus_shape_times_24_plus_text_times_23_plus_page_times_24(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_59_plus_shape_times_24_plus_text_times_23_plus_page_times_24(_SAMPLE)
        assert result == FN2_EXPECTED
