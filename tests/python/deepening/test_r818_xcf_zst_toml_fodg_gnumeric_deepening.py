"""Sprint R818 — FODG compound analytics deepening tests (Sprint 265)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_47_times_13_plus_shape_times_2200_plus_text_times_1800_plus_page_times_1100,
    fodg_file_size_times_12_plus_shape_times_100_plus_text_times_50_plus_page_times_25,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod47Times13PlusShapeTimes2200PlusTextTimes1800PlusPageTimes1100:
    def test_returns_int(self):
        result = fodg_file_size_mod_47_times_13_plus_shape_times_2200_plus_text_times_1800_plus_page_times_1100(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_47_times_13_plus_shape_times_2200_plus_text_times_1800_plus_page_times_1100(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_47_times_13_plus_shape_times_2200_plus_text_times_1800_plus_page_times_1100(_FODG)
        assert result == 1347

    def test_string_path(self):
        result = fodg_file_size_mod_47_times_13_plus_shape_times_2200_plus_text_times_1800_plus_page_times_1100(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_47_times_13_plus_shape_times_2200_plus_text_times_1800_plus_page_times_1100(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes12PlusShapeTimes100PlusTextTimes50PlusPageTimes25:
    def test_returns_int(self):
        result = fodg_file_size_times_12_plus_shape_times_100_plus_text_times_50_plus_page_times_25(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_12_plus_shape_times_100_plus_text_times_50_plus_page_times_25(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_12_plus_shape_times_100_plus_text_times_50_plus_page_times_25(_FODG)
        assert result == 12661

    def test_string_path(self):
        result = fodg_file_size_times_12_plus_shape_times_100_plus_text_times_50_plus_page_times_25(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_12_plus_shape_times_100_plus_text_times_50_plus_page_times_25(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
