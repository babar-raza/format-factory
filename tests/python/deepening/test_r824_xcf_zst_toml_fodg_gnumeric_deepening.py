"""Sprint R824 — FODG compound analytics deepening tests (Sprint 271)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_59_times_17_plus_shape_times_2600_plus_text_times_2200_plus_page_times_1300,
    fodg_file_size_times_14_plus_shape_times_30_plus_text_times_20_plus_page_times_10,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod59Times17PlusShapeTimes2600PlusTextTimes2200PlusPageTimes1300:
    def test_returns_int(self):
        result = fodg_file_size_mod_59_times_17_plus_shape_times_2600_plus_text_times_2200_plus_page_times_1300(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_59_times_17_plus_shape_times_2600_plus_text_times_2200_plus_page_times_1300(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_59_times_17_plus_shape_times_2600_plus_text_times_2200_plus_page_times_1300(_FODG)
        assert result == 2150

    def test_string_path(self):
        result = fodg_file_size_mod_59_times_17_plus_shape_times_2600_plus_text_times_2200_plus_page_times_1300(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_59_times_17_plus_shape_times_2600_plus_text_times_2200_plus_page_times_1300(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes14PlusShapeTimes30PlusTextTimes20PlusPageTimes10:
    def test_returns_int(self):
        result = fodg_file_size_times_14_plus_shape_times_30_plus_text_times_20_plus_page_times_10(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_14_plus_shape_times_30_plus_text_times_20_plus_page_times_10(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_14_plus_shape_times_30_plus_text_times_20_plus_page_times_10(_FODG)
        assert result == 14752

    def test_string_path(self):
        result = fodg_file_size_times_14_plus_shape_times_30_plus_text_times_20_plus_page_times_10(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_14_plus_shape_times_30_plus_text_times_20_plus_page_times_10(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
