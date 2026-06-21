"""Sprint R812 — FODG compound analytics deepening tests (Sprint 259)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_41_times_9_plus_shape_times_1800_plus_text_times_1400_plus_page_times_900,
    fodg_file_size_times_10_plus_shape_times_300_plus_text_times_150_plus_page_times_75,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod41Times9PlusShapeTimes1800PlusTextTimes1400PlusPageTimes900:
    def test_returns_int(self):
        result = fodg_file_size_mod_41_times_9_plus_shape_times_1800_plus_text_times_1400_plus_page_times_900(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_41_times_9_plus_shape_times_1800_plus_text_times_1400_plus_page_times_900(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_41_times_9_plus_shape_times_1800_plus_text_times_1400_plus_page_times_900(_FODG)
        assert result == 1152

    def test_string_path(self):
        result = fodg_file_size_mod_41_times_9_plus_shape_times_1800_plus_text_times_1400_plus_page_times_900(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_41_times_9_plus_shape_times_1800_plus_text_times_1400_plus_page_times_900(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes10PlusShapeTimes300PlusTextTimes150PlusPageTimes75:
    def test_returns_int(self):
        result = fodg_file_size_times_10_plus_shape_times_300_plus_text_times_150_plus_page_times_75(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_10_plus_shape_times_300_plus_text_times_150_plus_page_times_75(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_10_plus_shape_times_300_plus_text_times_150_plus_page_times_75(_FODG)
        assert result == 10605

    def test_string_path(self):
        result = fodg_file_size_times_10_plus_shape_times_300_plus_text_times_150_plus_page_times_75(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_10_plus_shape_times_300_plus_text_times_150_plus_page_times_75(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
