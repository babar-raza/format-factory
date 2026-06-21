"""Sprint R821 — FODG compound analytics deepening tests (Sprint 268)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_53_times_15_plus_shape_times_2400_plus_text_times_2000_plus_page_times_1200,
    fodg_file_size_times_13_plus_shape_times_50_plus_text_times_30_plus_page_times_15,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod53Times15PlusShapeTimes2400PlusTextTimes2000PlusPageTimes1200:
    def test_returns_int(self):
        result = fodg_file_size_mod_53_times_15_plus_shape_times_2400_plus_text_times_2000_plus_page_times_1200(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_53_times_15_plus_shape_times_2400_plus_text_times_2000_plus_page_times_1200(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_53_times_15_plus_shape_times_2400_plus_text_times_2000_plus_page_times_1200(_FODG)
        assert result == 1890

    def test_string_path(self):
        result = fodg_file_size_mod_53_times_15_plus_shape_times_2400_plus_text_times_2000_plus_page_times_1200(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_53_times_15_plus_shape_times_2400_plus_text_times_2000_plus_page_times_1200(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes13PlusShapeTimes50PlusTextTimes30PlusPageTimes15:
    def test_returns_int(self):
        result = fodg_file_size_times_13_plus_shape_times_50_plus_text_times_30_plus_page_times_15(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_13_plus_shape_times_50_plus_text_times_30_plus_page_times_15(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_13_plus_shape_times_50_plus_text_times_30_plus_page_times_15(_FODG)
        assert result == 13704

    def test_string_path(self):
        result = fodg_file_size_times_13_plus_shape_times_50_plus_text_times_30_plus_page_times_15(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_13_plus_shape_times_50_plus_text_times_30_plus_page_times_15(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
