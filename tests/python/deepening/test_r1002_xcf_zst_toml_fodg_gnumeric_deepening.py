"""Sprint 449 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_401_times_280_plus_shape_times_16600_plus_text_times_16200_plus_page_times_14500,
    fodg_file_size_times_147_plus_shape_times_63_plus_text_times_62_plus_page_times_63,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 84780
FN2_EXPECTED = 154854


class TestFodgFileSizeMod401Times280PlusShapeTimes16600PlusTextTimes16200PlusPageTimes14500:
    def test_returns_int(self):
        result = fodg_file_size_mod_401_times_280_plus_shape_times_16600_plus_text_times_16200_plus_page_times_14500(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_401_times_280_plus_shape_times_16600_plus_text_times_16200_plus_page_times_14500(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_401_times_280_plus_shape_times_16600_plus_text_times_16200_plus_page_times_14500(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_401_times_280_plus_shape_times_16600_plus_text_times_16200_plus_page_times_14500(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_401_times_280_plus_shape_times_16600_plus_text_times_16200_plus_page_times_14500(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes147PlusShapeTimes63PlusTextTimes62PlusPageTimes63:
    def test_returns_int(self):
        result = fodg_file_size_times_147_plus_shape_times_63_plus_text_times_62_plus_page_times_63(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_147_plus_shape_times_63_plus_text_times_62_plus_page_times_63(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_147_plus_shape_times_63_plus_text_times_62_plus_page_times_63(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_147_plus_shape_times_63_plus_text_times_62_plus_page_times_63(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_147_plus_shape_times_63_plus_text_times_62_plus_page_times_63(_SAMPLE)
        assert result == FN2_EXPECTED
