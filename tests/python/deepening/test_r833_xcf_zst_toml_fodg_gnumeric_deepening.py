"""Sprint R833 — FODG compound analytics deepening tests (Sprint 280)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_71_times_23_plus_shape_times_3200_plus_text_times_2800_plus_page_times_1600,
    fodg_file_size_times_17_plus_shape_times_8_plus_text_times_6_plus_page_times_4,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod71Times23PlusShapeTimes3200PlusTextTimes2800PlusPageTimes1600:
    def test_returns_int(self):
        result = fodg_file_size_mod_71_times_23_plus_shape_times_3200_plus_text_times_2800_plus_page_times_1600(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_71_times_23_plus_shape_times_3200_plus_text_times_2800_plus_page_times_1600(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_71_times_23_plus_shape_times_3200_plus_text_times_2800_plus_page_times_1600(_FODG)
        assert result == 2957

    def test_string_path(self):
        result = fodg_file_size_mod_71_times_23_plus_shape_times_3200_plus_text_times_2800_plus_page_times_1600(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_71_times_23_plus_shape_times_3200_plus_text_times_2800_plus_page_times_1600(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes17PlusShapeTimes8PlusTextTimes6PlusPageTimes4:
    def test_returns_int(self):
        result = fodg_file_size_times_17_plus_shape_times_8_plus_text_times_6_plus_page_times_4(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_17_plus_shape_times_8_plus_text_times_6_plus_page_times_4(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_17_plus_shape_times_8_plus_text_times_6_plus_page_times_4(_FODG)
        assert result == 17905

    def test_string_path(self):
        result = fodg_file_size_times_17_plus_shape_times_8_plus_text_times_6_plus_page_times_4(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_17_plus_shape_times_8_plus_text_times_6_plus_page_times_4(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
