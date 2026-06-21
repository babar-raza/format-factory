"""Sprint 511 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_491_times_355_plus_shape_times_19200_plus_text_times_18800_plus_page_times_17100,
    fodg_file_size_times_173_plus_shape_times_76_plus_text_times_75_plus_page_times_76,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 42305
FN2_EXPECTED = 182245


class TestFodgFileSizeMod491Times355PlusShapeTimes19200PlusTextTimes18800PlusPageTimes17100:
    def test_returns_int(self):
        result = fodg_file_size_mod_491_times_355_plus_shape_times_19200_plus_text_times_18800_plus_page_times_17100(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_491_times_355_plus_shape_times_19200_plus_text_times_18800_plus_page_times_17100(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_491_times_355_plus_shape_times_19200_plus_text_times_18800_plus_page_times_17100(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_491_times_355_plus_shape_times_19200_plus_text_times_18800_plus_page_times_17100(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_491_times_355_plus_shape_times_19200_plus_text_times_18800_plus_page_times_17100(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes173PlusShapeTimes76PlusTextTimes75PlusPageTimes76:
    def test_returns_int(self):
        result = fodg_file_size_times_173_plus_shape_times_76_plus_text_times_75_plus_page_times_76(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_173_plus_shape_times_76_plus_text_times_75_plus_page_times_76(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_173_plus_shape_times_76_plus_text_times_75_plus_page_times_76(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_173_plus_shape_times_76_plus_text_times_75_plus_page_times_76(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_173_plus_shape_times_76_plus_text_times_75_plus_page_times_76(_SAMPLE)
        assert result == FN2_EXPECTED
