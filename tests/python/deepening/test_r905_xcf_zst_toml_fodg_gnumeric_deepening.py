"""Sprint 352 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_217_times_80_plus_shape_times_8600_plus_text_times_8200_plus_page_times_6500,
    fodg_file_size_times_57_plus_shape_times_23_plus_text_times_22_plus_page_times_23,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 21300
FN2_EXPECTED = 60044


class TestFodgFileSizeMod217Times80PlusShapeTimes8600PlusTextTimes8200PlusPageTimes6500:
    def test_returns_int(self):
        result = fodg_file_size_mod_217_times_80_plus_shape_times_8600_plus_text_times_8200_plus_page_times_6500(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_217_times_80_plus_shape_times_8600_plus_text_times_8200_plus_page_times_6500(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_217_times_80_plus_shape_times_8600_plus_text_times_8200_plus_page_times_6500(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_217_times_80_plus_shape_times_8600_plus_text_times_8200_plus_page_times_6500(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_217_times_80_plus_shape_times_8600_plus_text_times_8200_plus_page_times_6500(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes57PlusShapeTimes23PlusTextTimes22PlusPageTimes23:
    def test_returns_int(self):
        result = fodg_file_size_times_57_plus_shape_times_23_plus_text_times_22_plus_page_times_23(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_57_plus_shape_times_23_plus_text_times_22_plus_page_times_23(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_57_plus_shape_times_23_plus_text_times_22_plus_page_times_23(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_57_plus_shape_times_23_plus_text_times_22_plus_page_times_23(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_57_plus_shape_times_23_plus_text_times_22_plus_page_times_23(_SAMPLE)
        assert result == FN2_EXPECTED
