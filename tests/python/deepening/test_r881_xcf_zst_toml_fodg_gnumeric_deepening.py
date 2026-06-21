"""Sprint R881 — FODG compound analytics deepening tests (Sprint 328)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_167_times_57_plus_shape_times_6400_plus_text_times_6000_plus_page_times_4300,
    fodg_file_size_times_38_plus_shape_times_12_plus_text_times_11_plus_page_times_12,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod167Times57PlusShapeTimes6400PlusTextTimes6000PlusPageTimes4300:
    def test_returns_int(self):
        result = fodg_file_size_mod_167_times_57_plus_shape_times_6400_plus_text_times_6000_plus_page_times_4300(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_167_times_57_plus_shape_times_6400_plus_text_times_6000_plus_page_times_4300(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_167_times_57_plus_shape_times_6400_plus_text_times_6000_plus_page_times_4300(_FODG)
        assert result == 7207

    def test_string_path(self):
        result = fodg_file_size_mod_167_times_57_plus_shape_times_6400_plus_text_times_6000_plus_page_times_4300(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_167_times_57_plus_shape_times_6400_plus_text_times_6000_plus_page_times_4300(
            SAMPLES / "fodg" / "empty-page.fodg"
        )
        assert isinstance(result, int)


class TestFodgFileSizeTimes38PlusShapeTimes12PlusTextTimes11PlusPageTimes12:
    def test_returns_int(self):
        result = fodg_file_size_times_38_plus_shape_times_12_plus_text_times_11_plus_page_times_12(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_38_plus_shape_times_12_plus_text_times_11_plus_page_times_12(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_38_plus_shape_times_12_plus_text_times_11_plus_page_times_12(_FODG)
        assert result == 40026

    def test_string_path(self):
        result = fodg_file_size_times_38_plus_shape_times_12_plus_text_times_11_plus_page_times_12(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_38_plus_shape_times_12_plus_text_times_11_plus_page_times_12(
            SAMPLES / "fodg" / "empty-page.fodg"
        )
        assert isinstance(result, int)
