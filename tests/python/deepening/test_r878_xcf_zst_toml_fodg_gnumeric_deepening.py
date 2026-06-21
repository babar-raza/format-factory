"""Sprint R878 — FODG compound analytics deepening tests (Sprint 325)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_163_times_55_plus_shape_times_6200_plus_text_times_5800_plus_page_times_4100,
    fodg_file_size_times_36_plus_shape_times_11_plus_text_times_10_plus_page_times_11,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod163Times55PlusShapeTimes6200PlusTextTimes5800PlusPageTimes4100:
    def test_returns_int(self):
        result = fodg_file_size_mod_163_times_55_plus_shape_times_6200_plus_text_times_5800_plus_page_times_4100(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_163_times_55_plus_shape_times_6200_plus_text_times_5800_plus_page_times_4100(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_163_times_55_plus_shape_times_6200_plus_text_times_5800_plus_page_times_4100(_FODG)
        assert result == 8225

    def test_string_path(self):
        result = fodg_file_size_mod_163_times_55_plus_shape_times_6200_plus_text_times_5800_plus_page_times_4100(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_163_times_55_plus_shape_times_6200_plus_text_times_5800_plus_page_times_4100(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes36PlusShapeTimes11PlusTextTimes10PlusPageTimes11:
    def test_returns_int(self):
        result = fodg_file_size_times_36_plus_shape_times_11_plus_text_times_10_plus_page_times_11(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_36_plus_shape_times_11_plus_text_times_10_plus_page_times_11(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_36_plus_shape_times_11_plus_text_times_10_plus_page_times_11(_FODG)
        assert result == 37919

    def test_string_path(self):
        result = fodg_file_size_times_36_plus_shape_times_11_plus_text_times_10_plus_page_times_11(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_36_plus_shape_times_11_plus_text_times_10_plus_page_times_11(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
