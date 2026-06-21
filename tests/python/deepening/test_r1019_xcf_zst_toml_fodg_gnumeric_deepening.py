"""Sprint 466 - FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_389_times_270_plus_shape_times_16200_plus_text_times_15800_plus_page_times_14100,
    fodg_file_size_times_143_plus_shape_times_61_plus_text_times_60_plus_page_times_61,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 88350
FN2_EXPECTED = 150640


class TestFodgFileSizeMod389Times270PlusShapeTimes16200PlusTextTimes15800PlusPageTimes14100:
    def test_returns_int(self):
        result = fodg_file_size_mod_389_times_270_plus_shape_times_16200_plus_text_times_15800_plus_page_times_14100(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_389_times_270_plus_shape_times_16200_plus_text_times_15800_plus_page_times_14100(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_389_times_270_plus_shape_times_16200_plus_text_times_15800_plus_page_times_14100(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_389_times_270_plus_shape_times_16200_plus_text_times_15800_plus_page_times_14100(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_389_times_270_plus_shape_times_16200_plus_text_times_15800_plus_page_times_14100(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes143PlusShapeTimes61PlusTextTimes60PlusPageTimes61:
    def test_returns_int(self):
        result = fodg_file_size_times_143_plus_shape_times_61_plus_text_times_60_plus_page_times_61(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_143_plus_shape_times_61_plus_text_times_60_plus_page_times_61(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_143_plus_shape_times_61_plus_text_times_60_plus_page_times_61(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_143_plus_shape_times_61_plus_text_times_60_plus_page_times_61(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_143_plus_shape_times_61_plus_text_times_60_plus_page_times_61(_SAMPLE)
        assert result == FN2_EXPECTED
