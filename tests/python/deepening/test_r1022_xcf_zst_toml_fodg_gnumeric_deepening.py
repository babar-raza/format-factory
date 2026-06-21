"""Sprint 469 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_397_times_275_plus_shape_times_16400_plus_text_times_16000_plus_page_times_14300,
    fodg_file_size_times_145_plus_shape_times_62_plus_text_times_61_plus_page_times_62,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 85525
FN2_EXPECTED = 152747


class TestFodgFileSizeMod397Times275PlusShapeTimes16400PlusTextTimes16000PlusPageTimes14300:
    def test_returns_int(self):
        result = fodg_file_size_mod_397_times_275_plus_shape_times_16400_plus_text_times_16000_plus_page_times_14300(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_397_times_275_plus_shape_times_16400_plus_text_times_16000_plus_page_times_14300(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_397_times_275_plus_shape_times_16400_plus_text_times_16000_plus_page_times_14300(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_397_times_275_plus_shape_times_16400_plus_text_times_16000_plus_page_times_14300(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_397_times_275_plus_shape_times_16400_plus_text_times_16000_plus_page_times_14300(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes145PlusShapeTimes62PlusTextTimes61PlusPageTimes62:
    def test_returns_int(self):
        result = fodg_file_size_times_145_plus_shape_times_62_plus_text_times_61_plus_page_times_62(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_145_plus_shape_times_62_plus_text_times_61_plus_page_times_62(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_145_plus_shape_times_62_plus_text_times_61_plus_page_times_62(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_145_plus_shape_times_62_plus_text_times_61_plus_page_times_62(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_145_plus_shape_times_62_plus_text_times_61_plus_page_times_62(_SAMPLE)
        assert result == FN2_EXPECTED
