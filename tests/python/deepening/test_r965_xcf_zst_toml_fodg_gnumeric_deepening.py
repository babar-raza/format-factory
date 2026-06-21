"""Sprint 412 — FODG deepening: 2 compound analytics functions, 10 tests."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_mod_305_times_180_plus_shape_times_12600_plus_text_times_12200_plus_page_times_10500,
    fodg_file_size_times_103_plus_shape_times_42_plus_text_times_41_plus_page_times_42,
)

_SAMPLE = _REPO / "samples/by-format/fodg/empty-page.fodg"

FN1_EXPECTED = 35340
FN2_EXPECTED = 108501


class TestFodgFileSizeMod305Times180PlusShapeTimes12600PlusTextTimes12200PlusPageTimes10500:
    def test_returns_int(self):
        result = fodg_file_size_mod_305_times_180_plus_shape_times_12600_plus_text_times_12200_plus_page_times_10500(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_mod_305_times_180_plus_shape_times_12600_plus_text_times_12200_plus_page_times_10500(_SAMPLE)
        assert result == FN1_EXPECTED

    def test_positive(self):
        result = fodg_file_size_mod_305_times_180_plus_shape_times_12600_plus_text_times_12200_plus_page_times_10500(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_mod_305_times_180_plus_shape_times_12600_plus_text_times_12200_plus_page_times_10500(str(_SAMPLE))
        assert result == FN1_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_mod_305_times_180_plus_shape_times_12600_plus_text_times_12200_plus_page_times_10500(_SAMPLE)
        assert result == FN1_EXPECTED


class TestFodgFileSizeTimes103PlusShapeTimes42PlusTextTimes41PlusPageTimes42:
    def test_returns_int(self):
        result = fodg_file_size_times_103_plus_shape_times_42_plus_text_times_41_plus_page_times_42(_SAMPLE)
        assert isinstance(result, int)

    def test_expected_value(self):
        result = fodg_file_size_times_103_plus_shape_times_42_plus_text_times_41_plus_page_times_42(_SAMPLE)
        assert result == FN2_EXPECTED

    def test_positive(self):
        result = fodg_file_size_times_103_plus_shape_times_42_plus_text_times_41_plus_page_times_42(_SAMPLE)
        assert result > 0

    def test_accepts_str_path(self):
        result = fodg_file_size_times_103_plus_shape_times_42_plus_text_times_41_plus_page_times_42(str(_SAMPLE))
        assert result == FN2_EXPECTED

    def test_accepts_path_object(self):
        result = fodg_file_size_times_103_plus_shape_times_42_plus_text_times_41_plus_page_times_42(_SAMPLE)
        assert result == FN2_EXPECTED
