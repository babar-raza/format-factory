"""Sprint 397 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_287_times_155_plus_shape_times_11600_plus_text_times_11200_plus_page_times_9500,
    fodg_file_size_times_93_plus_shape_times_37_plus_text_times_36_plus_page_times_37,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 39260
FN2_EXPECTED = 97966


class TestFodgFileSizeMod287Times155PlusShapeTimes11600PlusTextTimes11200PlusPageTimes9500:
    def test_returns_int(self):
        result = fodg_file_size_mod_287_times_155_plus_shape_times_11600_plus_text_times_11200_plus_page_times_9500(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_287_times_155_plus_shape_times_11600_plus_text_times_11200_plus_page_times_9500(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_287_times_155_plus_shape_times_11600_plus_text_times_11200_plus_page_times_9500(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_287_times_155_plus_shape_times_11600_plus_text_times_11200_plus_page_times_9500(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_287_times_155_plus_shape_times_11600_plus_text_times_11200_plus_page_times_9500(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes93PlusShapeTimes37PlusTextTimes36PlusPageTimes37:
    def test_returns_int(self):
        result = fodg_file_size_times_93_plus_shape_times_37_plus_text_times_36_plus_page_times_37(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_93_plus_shape_times_37_plus_text_times_36_plus_page_times_37(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_93_plus_shape_times_37_plus_text_times_36_plus_page_times_37(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_93_plus_shape_times_37_plus_text_times_36_plus_page_times_37(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_93_plus_shape_times_37_plus_text_times_36_plus_page_times_37(_SAMPLE)
        assert result == FN2_EXPECTED
