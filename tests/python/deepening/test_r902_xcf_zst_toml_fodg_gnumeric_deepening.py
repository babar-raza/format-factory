"""Sprint R902 — FODG compound analytics deepening tests (Sprint 349)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_213_times_75_plus_shape_times_8400_plus_text_times_8000_plus_page_times_6300,
    fodg_file_size_times_55_plus_shape_times_22_plus_text_times_21_plus_page_times_22,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod213Times75PlusShapeTimes8400PlusTextTimes8000PlusPageTimes6300:
    def test_returns_int(self):
        result = fodg_file_size_mod_213_times_75_plus_shape_times_8400_plus_text_times_8000_plus_page_times_6300(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_213_times_75_plus_shape_times_8400_plus_text_times_8000_plus_page_times_6300(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_213_times_75_plus_shape_times_8400_plus_text_times_8000_plus_page_times_6300(_FODG)
        assert result == 21375

    def test_string_path(self):
        result = fodg_file_size_mod_213_times_75_plus_shape_times_8400_plus_text_times_8000_plus_page_times_6300(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_213_times_75_plus_shape_times_8400_plus_text_times_8000_plus_page_times_6300(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes55PlusShapeTimes22PlusTextTimes21PlusPageTimes22:
    def test_returns_int(self):
        result = fodg_file_size_times_55_plus_shape_times_22_plus_text_times_21_plus_page_times_22(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_55_plus_shape_times_22_plus_text_times_21_plus_page_times_22(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_55_plus_shape_times_22_plus_text_times_21_plus_page_times_22(_FODG)
        assert result == 57937

    def test_string_path(self):
        result = fodg_file_size_times_55_plus_shape_times_22_plus_text_times_21_plus_page_times_22(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_55_plus_shape_times_22_plus_text_times_21_plus_page_times_22(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
