"""Sprint R860 — FODG compound analytics deepening tests (Sprint 307)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_127_times_43_plus_shape_times_5000_plus_text_times_4600_plus_page_times_2900,
    fodg_file_size_times_27_plus_shape_times_5_plus_text_times_4_plus_page_times_5,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod127Times43PlusShapeTimes5000PlusTextTimes4600PlusPageTimes2900:
    def test_returns_int(self):
        result = fodg_file_size_mod_127_times_43_plus_shape_times_5000_plus_text_times_4600_plus_page_times_2900(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_127_times_43_plus_shape_times_5000_plus_text_times_4600_plus_page_times_2900(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_127_times_43_plus_shape_times_5000_plus_text_times_4600_plus_page_times_2900(_FODG)
        assert result == 4491

    def test_string_path(self):
        result = fodg_file_size_mod_127_times_43_plus_shape_times_5000_plus_text_times_4600_plus_page_times_2900(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_127_times_43_plus_shape_times_5000_plus_text_times_4600_plus_page_times_2900(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes27PlusShapeTimes5PlusTextTimes4PlusPageTimes5:
    def test_returns_int(self):
        result = fodg_file_size_times_27_plus_shape_times_5_plus_text_times_4_plus_page_times_5(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_27_plus_shape_times_5_plus_text_times_4_plus_page_times_5(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_27_plus_shape_times_5_plus_text_times_4_plus_page_times_5(_FODG)
        assert result == 28436

    def test_string_path(self):
        result = fodg_file_size_times_27_plus_shape_times_5_plus_text_times_4_plus_page_times_5(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_27_plus_shape_times_5_plus_text_times_4_plus_page_times_5(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
