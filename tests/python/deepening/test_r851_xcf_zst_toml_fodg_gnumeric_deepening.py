"""Sprint R851 — FODG compound analytics deepening tests (Sprint 298)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_107_times_37_plus_shape_times_4400_plus_text_times_4000_plus_page_times_2300,
    fodg_file_size_times_24_plus_shape_times_2_plus_text_times_2_plus_page_times_2,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod107Times37PlusShapeTimes4400PlusTextTimes4000PlusPageTimes2300:
    def test_returns_int(self):
        result = fodg_file_size_mod_107_times_37_plus_shape_times_4400_plus_text_times_4000_plus_page_times_2300(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_107_times_37_plus_shape_times_4400_plus_text_times_4000_plus_page_times_2300(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_107_times_37_plus_shape_times_4400_plus_text_times_4000_plus_page_times_2300(_FODG)
        assert result == 5630

    def test_string_path(self):
        result = fodg_file_size_mod_107_times_37_plus_shape_times_4400_plus_text_times_4000_plus_page_times_2300(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_107_times_37_plus_shape_times_4400_plus_text_times_4000_plus_page_times_2300(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes24PlusShapeTimes2PlusTextTimes2PlusPageTimes2:
    def test_returns_int(self):
        result = fodg_file_size_times_24_plus_shape_times_2_plus_text_times_2_plus_page_times_2(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_24_plus_shape_times_2_plus_text_times_2_plus_page_times_2(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_24_plus_shape_times_2_plus_text_times_2_plus_page_times_2(_FODG)
        assert result == 25274

    def test_string_path(self):
        result = fodg_file_size_times_24_plus_shape_times_2_plus_text_times_2_plus_page_times_2(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_24_plus_shape_times_2_plus_text_times_2_plus_page_times_2(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
