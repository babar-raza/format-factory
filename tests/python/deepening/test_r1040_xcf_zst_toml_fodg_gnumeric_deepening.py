"""Sprint 487 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_433_times_310_plus_shape_times_17600_plus_text_times_17200_plus_page_times_15500,
    fodg_file_size_times_157_plus_shape_times_68_plus_text_times_67_plus_page_times_68,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 73470
FN2_EXPECTED = 165389


class TestFodgFileSizeMod433Times310PlusShapeTimes17600PlusTextTimes17200PlusPageTimes15500:
    def test_returns_int(self):
        result = fodg_file_size_mod_433_times_310_plus_shape_times_17600_plus_text_times_17200_plus_page_times_15500(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_433_times_310_plus_shape_times_17600_plus_text_times_17200_plus_page_times_15500(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_433_times_310_plus_shape_times_17600_plus_text_times_17200_plus_page_times_15500(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_433_times_310_plus_shape_times_17600_plus_text_times_17200_plus_page_times_15500(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_433_times_310_plus_shape_times_17600_plus_text_times_17200_plus_page_times_15500(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes157PlusShapeTimes68PlusTextTimes67PlusPageTimes68:
    def test_returns_int(self):
        result = fodg_file_size_times_157_plus_shape_times_68_plus_text_times_67_plus_page_times_68(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_157_plus_shape_times_68_plus_text_times_67_plus_page_times_68(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_157_plus_shape_times_68_plus_text_times_67_plus_page_times_68(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_157_plus_shape_times_68_plus_text_times_67_plus_page_times_68(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_157_plus_shape_times_68_plus_text_times_67_plus_page_times_68(_SAMPLE)
        assert result == FN2_EXPECTED
