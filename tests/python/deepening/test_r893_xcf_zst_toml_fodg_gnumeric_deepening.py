"""Sprint R893 — FODG compound analytics deepening tests (Sprint 340)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_197_times_69_plus_shape_times_7800_plus_text_times_7400_plus_page_times_5700,
    fodg_file_size_times_49_plus_shape_times_19_plus_text_times_18_plus_page_times_19,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod197Times69PlusShapeTimes7800PlusTextTimes7400PlusPageTimes5700:
    def test_returns_int(self):
        result = fodg_file_size_mod_197_times_69_plus_shape_times_7800_plus_text_times_7400_plus_page_times_5700(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_197_times_69_plus_shape_times_7800_plus_text_times_7400_plus_page_times_5700(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_197_times_69_plus_shape_times_7800_plus_text_times_7400_plus_page_times_5700(_FODG)
        assert result == 10392

    def test_string_path(self):
        result = fodg_file_size_mod_197_times_69_plus_shape_times_7800_plus_text_times_7400_plus_page_times_5700(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_197_times_69_plus_shape_times_7800_plus_text_times_7400_plus_page_times_5700(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes49PlusShapeTimes19PlusTextTimes18PlusPageTimes19:
    def test_returns_int(self):
        result = fodg_file_size_times_49_plus_shape_times_19_plus_text_times_18_plus_page_times_19(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_49_plus_shape_times_19_plus_text_times_18_plus_page_times_19(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_49_plus_shape_times_19_plus_text_times_18_plus_page_times_19(_FODG)
        assert result == 51616

    def test_string_path(self):
        result = fodg_file_size_times_49_plus_shape_times_19_plus_text_times_18_plus_page_times_19(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_49_plus_shape_times_19_plus_text_times_18_plus_page_times_19(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
