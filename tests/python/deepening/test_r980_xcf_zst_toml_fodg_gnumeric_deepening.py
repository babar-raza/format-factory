"""Sprint 427 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_325_times_205_plus_shape_times_13600_plus_text_times_13200_plus_page_times_11500,
    fodg_file_size_times_115_plus_shape_times_47_plus_text_times_46_plus_page_times_47,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 27490
FN2_EXPECTED = 121142


class TestFodgFileSizeMod325Times205PlusShapeTimes13600PlusTextTimes13200PlusPageTimes11500:
    def test_returns_int(self):
        result = fodg_file_size_mod_325_times_205_plus_shape_times_13600_plus_text_times_13200_plus_page_times_11500(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_325_times_205_plus_shape_times_13600_plus_text_times_13200_plus_page_times_11500(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_325_times_205_plus_shape_times_13600_plus_text_times_13200_plus_page_times_11500(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_325_times_205_plus_shape_times_13600_plus_text_times_13200_plus_page_times_11500(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_325_times_205_plus_shape_times_13600_plus_text_times_13200_plus_page_times_11500(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes115PlusShapeTimes47PlusTextTimes46PlusPageTimes47:
    def test_returns_int(self):
        result = fodg_file_size_times_115_plus_shape_times_47_plus_text_times_46_plus_page_times_47(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_115_plus_shape_times_47_plus_text_times_46_plus_page_times_47(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_115_plus_shape_times_47_plus_text_times_46_plus_page_times_47(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_115_plus_shape_times_47_plus_text_times_46_plus_page_times_47(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_115_plus_shape_times_47_plus_text_times_46_plus_page_times_47(_SAMPLE)
        assert result == FN2_EXPECTED
