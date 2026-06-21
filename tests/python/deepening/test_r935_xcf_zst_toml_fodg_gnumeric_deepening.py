"""Sprint 382 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_257_times_130_plus_shape_times_10600_plus_text_times_10200_plus_page_times_8500,
    fodg_file_size_times_83_plus_shape_times_33_plus_text_times_32_plus_page_times_33,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 11750
FN2_EXPECTED = 87432


class TestFodgFileSizeMod257Times130PlusShapeTimes10600PlusTextTimes10200PlusPageTimes8500:
    def test_returns_int(self):
        result = fodg_file_size_mod_257_times_130_plus_shape_times_10600_plus_text_times_10200_plus_page_times_8500(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_257_times_130_plus_shape_times_10600_plus_text_times_10200_plus_page_times_8500(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_257_times_130_plus_shape_times_10600_plus_text_times_10200_plus_page_times_8500(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_257_times_130_plus_shape_times_10600_plus_text_times_10200_plus_page_times_8500(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_257_times_130_plus_shape_times_10600_plus_text_times_10200_plus_page_times_8500(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes83PlusShapeTimes33PlusTextTimes32PlusPageTimes33:
    def test_returns_int(self):
        result = fodg_file_size_times_83_plus_shape_times_33_plus_text_times_32_plus_page_times_33(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_83_plus_shape_times_33_plus_text_times_32_plus_page_times_33(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_83_plus_shape_times_33_plus_text_times_32_plus_page_times_33(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_83_plus_shape_times_33_plus_text_times_32_plus_page_times_33(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_83_plus_shape_times_33_plus_text_times_32_plus_page_times_33(_SAMPLE)
        assert result == FN2_EXPECTED
