"""Sprint 400 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_289_times_160_plus_shape_times_11800_plus_text_times_11400_plus_page_times_9700,
    fodg_file_size_times_95_plus_shape_times_38_plus_text_times_37_plus_page_times_38,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 39460
FN2_EXPECTED = 100073


class TestFodgFileSizeMod289Times160PlusShapeTimes11800PlusTextTimes11400PlusPageTimes9700:
    def test_returns_int(self):
        result = fodg_file_size_mod_289_times_160_plus_shape_times_11800_plus_text_times_11400_plus_page_times_9700(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_289_times_160_plus_shape_times_11800_plus_text_times_11400_plus_page_times_9700(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_289_times_160_plus_shape_times_11800_plus_text_times_11400_plus_page_times_9700(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_289_times_160_plus_shape_times_11800_plus_text_times_11400_plus_page_times_9700(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_289_times_160_plus_shape_times_11800_plus_text_times_11400_plus_page_times_9700(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes95PlusShapeTimes38PlusTextTimes37PlusPageTimes38:
    def test_returns_int(self):
        result = fodg_file_size_times_95_plus_shape_times_38_plus_text_times_37_plus_page_times_38(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_95_plus_shape_times_38_plus_text_times_37_plus_page_times_38(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_95_plus_shape_times_38_plus_text_times_37_plus_page_times_38(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_95_plus_shape_times_38_plus_text_times_37_plus_page_times_38(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_95_plus_shape_times_38_plus_text_times_37_plus_page_times_38(_SAMPLE)
        assert result == FN2_EXPECTED
