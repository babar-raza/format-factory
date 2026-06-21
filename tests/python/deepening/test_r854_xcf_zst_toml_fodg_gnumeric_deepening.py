"""Sprint R854 — FODG compound analytics deepening tests (Sprint 301)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_109_times_39_plus_shape_times_4600_plus_text_times_4200_plus_page_times_2500,
    fodg_file_size_times_25_plus_shape_times_3_plus_text_times_2_plus_page_times_3,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod109Times39PlusShapeTimes4600PlusTextTimes4200PlusPageTimes2500:
    def test_returns_int(self):
        result = fodg_file_size_mod_109_times_39_plus_shape_times_4600_plus_text_times_4200_plus_page_times_2500(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_109_times_39_plus_shape_times_4600_plus_text_times_4200_plus_page_times_2500(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_109_times_39_plus_shape_times_4600_plus_text_times_4200_plus_page_times_2500(_FODG)
        assert result == 5308

    def test_string_path(self):
        result = fodg_file_size_mod_109_times_39_plus_shape_times_4600_plus_text_times_4200_plus_page_times_2500(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_109_times_39_plus_shape_times_4600_plus_text_times_4200_plus_page_times_2500(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes25PlusShapeTimes3PlusTextTimes2PlusPageTimes3:
    def test_returns_int(self):
        result = fodg_file_size_times_25_plus_shape_times_3_plus_text_times_2_plus_page_times_3(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_25_plus_shape_times_3_plus_text_times_2_plus_page_times_3(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_25_plus_shape_times_3_plus_text_times_2_plus_page_times_3(_FODG)
        assert result == 26328

    def test_string_path(self):
        result = fodg_file_size_times_25_plus_shape_times_3_plus_text_times_2_plus_page_times_3(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_25_plus_shape_times_3_plus_text_times_2_plus_page_times_3(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
