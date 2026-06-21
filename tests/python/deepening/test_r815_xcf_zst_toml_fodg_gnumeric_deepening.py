"""Sprint R815 — FODG compound analytics deepening tests (Sprint 262)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_43_times_11_plus_shape_times_2000_plus_text_times_1600_plus_page_times_1000,
    fodg_file_size_times_11_plus_shape_times_200_plus_text_times_100_plus_page_times_50,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod43Times11PlusShapeTimes2000PlusTextTimes1600PlusPageTimes1000:
    def test_returns_int(self):
        result = fodg_file_size_mod_43_times_11_plus_shape_times_2000_plus_text_times_1600_plus_page_times_1000(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_43_times_11_plus_shape_times_2000_plus_text_times_1600_plus_page_times_1000(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_43_times_11_plus_shape_times_2000_plus_text_times_1600_plus_page_times_1000(_FODG)
        assert result == 1231

    def test_string_path(self):
        result = fodg_file_size_mod_43_times_11_plus_shape_times_2000_plus_text_times_1600_plus_page_times_1000(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_43_times_11_plus_shape_times_2000_plus_text_times_1600_plus_page_times_1000(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes11PlusShapeTimes200PlusTextTimes100PlusPageTimes50:
    def test_returns_int(self):
        result = fodg_file_size_times_11_plus_shape_times_200_plus_text_times_100_plus_page_times_50(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_11_plus_shape_times_200_plus_text_times_100_plus_page_times_50(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_11_plus_shape_times_200_plus_text_times_100_plus_page_times_50(_FODG)
        assert result == 11633

    def test_string_path(self):
        result = fodg_file_size_times_11_plus_shape_times_200_plus_text_times_100_plus_page_times_50(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_11_plus_shape_times_200_plus_text_times_100_plus_page_times_50(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
