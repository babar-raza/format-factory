"""Sprint R896 — FODG compound analytics deepening tests (Sprint 343)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_199_times_71_plus_shape_times_8000_plus_text_times_7600_plus_page_times_5900,
    fodg_file_size_times_51_plus_shape_times_20_plus_text_times_19_plus_page_times_20,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod199Times71PlusShapeTimes8000PlusTextTimes7600PlusPageTimes5900:
    def test_returns_int(self):
        result = fodg_file_size_mod_199_times_71_plus_shape_times_8000_plus_text_times_7600_plus_page_times_5900(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_199_times_71_plus_shape_times_8000_plus_text_times_7600_plus_page_times_5900(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_199_times_71_plus_shape_times_8000_plus_text_times_7600_plus_page_times_5900(_FODG)
        assert result == 10018

    def test_string_path(self):
        result = fodg_file_size_mod_199_times_71_plus_shape_times_8000_plus_text_times_7600_plus_page_times_5900(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_199_times_71_plus_shape_times_8000_plus_text_times_7600_plus_page_times_5900(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes51PlusShapeTimes20PlusTextTimes19PlusPageTimes20:
    def test_returns_int(self):
        result = fodg_file_size_times_51_plus_shape_times_20_plus_text_times_19_plus_page_times_20(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_51_plus_shape_times_20_plus_text_times_19_plus_page_times_20(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_51_plus_shape_times_20_plus_text_times_19_plus_page_times_20(_FODG)
        assert result == 53723

    def test_string_path(self):
        result = fodg_file_size_times_51_plus_shape_times_20_plus_text_times_19_plus_page_times_20(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_51_plus_shape_times_20_plus_text_times_19_plus_page_times_20(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
