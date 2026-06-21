"""Sprint 502 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_467_times_340_plus_shape_times_18600_plus_text_times_18200_plus_page_times_16500,
    fodg_file_size_times_167_plus_shape_times_73_plus_text_times_72_plus_page_times_73,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 56960
FN2_EXPECTED = 175924


class TestFodgFileSizeMod467Times340PlusShapeTimes18600PlusTextTimes18200PlusPageTimes16500:
    def test_returns_int(self):
        result = fodg_file_size_mod_467_times_340_plus_shape_times_18600_plus_text_times_18200_plus_page_times_16500(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_467_times_340_plus_shape_times_18600_plus_text_times_18200_plus_page_times_16500(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_467_times_340_plus_shape_times_18600_plus_text_times_18200_plus_page_times_16500(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_467_times_340_plus_shape_times_18600_plus_text_times_18200_plus_page_times_16500(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_467_times_340_plus_shape_times_18600_plus_text_times_18200_plus_page_times_16500(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes167PlusShapeTimes73PlusTextTimes72PlusPageTimes73:
    def test_returns_int(self):
        result = fodg_file_size_times_167_plus_shape_times_73_plus_text_times_72_plus_page_times_73(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_167_plus_shape_times_73_plus_text_times_72_plus_page_times_73(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_167_plus_shape_times_73_plus_text_times_72_plus_page_times_73(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_167_plus_shape_times_73_plus_text_times_72_plus_page_times_73(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_167_plus_shape_times_73_plus_text_times_72_plus_page_times_73(_SAMPLE)
        assert result == FN2_EXPECTED
