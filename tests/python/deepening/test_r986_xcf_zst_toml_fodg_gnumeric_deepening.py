"""Sprint 433 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_329_times_215_plus_shape_times_14000_plus_text_times_13600_plus_page_times_11900,
    fodg_file_size_times_119_plus_shape_times_49_plus_text_times_48_plus_page_times_49,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 26090
FN2_EXPECTED = 125356


class TestFodgFileSizeMod329Times215PlusShapeTimes14000PlusTextTimes13600PlusPageTimes11900:
    def test_returns_int(self):
        result = fodg_file_size_mod_329_times_215_plus_shape_times_14000_plus_text_times_13600_plus_page_times_11900(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_329_times_215_plus_shape_times_14000_plus_text_times_13600_plus_page_times_11900(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_329_times_215_plus_shape_times_14000_plus_text_times_13600_plus_page_times_11900(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_329_times_215_plus_shape_times_14000_plus_text_times_13600_plus_page_times_11900(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_329_times_215_plus_shape_times_14000_plus_text_times_13600_plus_page_times_11900(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes119PlusShapeTimes49PlusTextTimes48PlusPageTimes49:
    def test_returns_int(self):
        result = fodg_file_size_times_119_plus_shape_times_49_plus_text_times_48_plus_page_times_49(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_119_plus_shape_times_49_plus_text_times_48_plus_page_times_49(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_119_plus_shape_times_49_plus_text_times_48_plus_page_times_49(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_119_plus_shape_times_49_plus_text_times_48_plus_page_times_49(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_119_plus_shape_times_49_plus_text_times_48_plus_page_times_49(_SAMPLE)
        assert result == FN2_EXPECTED
