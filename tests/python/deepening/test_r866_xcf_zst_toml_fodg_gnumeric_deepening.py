"""Sprint R866 — FODG compound analytics deepening tests (Sprint 313)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_139_times_47_plus_shape_times_5400_plus_text_times_5000_plus_page_times_3300,
    fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod139Times47PlusShapeTimes5400PlusTextTimes5000PlusPageTimes3300:
    def test_returns_int(self):
        result = fodg_file_size_mod_139_times_47_plus_shape_times_5400_plus_text_times_5000_plus_page_times_3300(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_139_times_47_plus_shape_times_5400_plus_text_times_5000_plus_page_times_3300(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_139_times_47_plus_shape_times_5400_plus_text_times_5000_plus_page_times_3300(_FODG)
        assert result == 7060

    def test_string_path(self):
        result = fodg_file_size_mod_139_times_47_plus_shape_times_5400_plus_text_times_5000_plus_page_times_3300(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_139_times_47_plus_shape_times_5400_plus_text_times_5000_plus_page_times_3300(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes29PlusShapeTimes7PlusTextTimes6PlusPageTimes7:
    def test_returns_int(self):
        result = fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7(_FODG)
        assert result == 30544

    def test_string_path(self):
        result = fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_29_plus_shape_times_7_plus_text_times_6_plus_page_times_7(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
