"""Sprint R857 — FODG compound analytics deepening tests (Sprint 304)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_113_times_41_plus_shape_times_4800_plus_text_times_4400_plus_page_times_2700,
    fodg_file_size_times_26_plus_shape_times_4_plus_text_times_3_plus_page_times_4,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod113Times41PlusShapeTimes4800PlusTextTimes4400PlusPageTimes2700:
    def test_returns_int(self):
        result = fodg_file_size_mod_113_times_41_plus_shape_times_4800_plus_text_times_4400_plus_page_times_2700(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_113_times_41_plus_shape_times_4800_plus_text_times_4400_plus_page_times_2700(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_113_times_41_plus_shape_times_4800_plus_text_times_4400_plus_page_times_2700(_FODG)
        assert result == 4176

    def test_string_path(self):
        result = fodg_file_size_mod_113_times_41_plus_shape_times_4800_plus_text_times_4400_plus_page_times_2700(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_113_times_41_plus_shape_times_4800_plus_text_times_4400_plus_page_times_2700(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes26PlusShapeTimes4PlusTextTimes3PlusPageTimes4:
    def test_returns_int(self):
        result = fodg_file_size_times_26_plus_shape_times_4_plus_text_times_3_plus_page_times_4(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_26_plus_shape_times_4_plus_text_times_3_plus_page_times_4(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_26_plus_shape_times_4_plus_text_times_3_plus_page_times_4(_FODG)
        assert result == 27382

    def test_string_path(self):
        result = fodg_file_size_times_26_plus_shape_times_4_plus_text_times_3_plus_page_times_4(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_26_plus_shape_times_4_plus_text_times_3_plus_page_times_4(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
