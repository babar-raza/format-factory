"""Sprint R842 — FODG compound analytics deepening tests (Sprint 289)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_89_times_29_plus_shape_times_3800_plus_text_times_3400_plus_page_times_1900,
    fodg_file_size_times_21_plus_shape_times_3_plus_text_times_2_plus_page_times_1,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod89Times29PlusShapeTimes3800PlusTextTimes3400PlusPageTimes1900:
    def test_returns_int(self):
        result = fodg_file_size_mod_89_times_29_plus_shape_times_3800_plus_text_times_3400_plus_page_times_1900(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_89_times_29_plus_shape_times_3800_plus_text_times_3400_plus_page_times_1900(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_89_times_29_plus_shape_times_3800_plus_text_times_3400_plus_page_times_1900(_FODG)
        assert result == 4046

    def test_string_path(self):
        result = fodg_file_size_mod_89_times_29_plus_shape_times_3800_plus_text_times_3400_plus_page_times_1900(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_89_times_29_plus_shape_times_3800_plus_text_times_3400_plus_page_times_1900(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes21PlusShapeTimes3PlusTextTimes2PlusPageTimes1:
    def test_returns_int(self):
        result = fodg_file_size_times_21_plus_shape_times_3_plus_text_times_2_plus_page_times_1(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_21_plus_shape_times_3_plus_text_times_2_plus_page_times_1(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_21_plus_shape_times_3_plus_text_times_2_plus_page_times_1(_FODG)
        assert result == 22114

    def test_string_path(self):
        result = fodg_file_size_times_21_plus_shape_times_3_plus_text_times_2_plus_page_times_1(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_21_plus_shape_times_3_plus_text_times_2_plus_page_times_1(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
