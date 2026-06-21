"""Sprint R836 — FODG compound analytics deepening tests (Sprint 283)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_79_times_25_plus_shape_times_3400_plus_text_times_3000_plus_page_times_1700,
    fodg_file_size_times_19_plus_shape_times_6_plus_text_times_4_plus_page_times_2,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod79Times25PlusShapeTimes3400PlusTextTimes3000PlusPageTimes1700:
    def test_returns_int(self):
        result = fodg_file_size_mod_79_times_25_plus_shape_times_3400_plus_text_times_3000_plus_page_times_1700(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_79_times_25_plus_shape_times_3400_plus_text_times_3000_plus_page_times_1700(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_79_times_25_plus_shape_times_3400_plus_text_times_3000_plus_page_times_1700(_FODG)
        assert result == 2350

    def test_string_path(self):
        result = fodg_file_size_mod_79_times_25_plus_shape_times_3400_plus_text_times_3000_plus_page_times_1700(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_79_times_25_plus_shape_times_3400_plus_text_times_3000_plus_page_times_1700(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes19PlusShapeTimes6PlusTextTimes4PlusPageTimes2:
    def test_returns_int(self):
        result = fodg_file_size_times_19_plus_shape_times_6_plus_text_times_4_plus_page_times_2(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_19_plus_shape_times_6_plus_text_times_4_plus_page_times_2(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_19_plus_shape_times_6_plus_text_times_4_plus_page_times_2(_FODG)
        assert result == 20009

    def test_string_path(self):
        result = fodg_file_size_times_19_plus_shape_times_6_plus_text_times_4_plus_page_times_2(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_19_plus_shape_times_6_plus_text_times_4_plus_page_times_2(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
