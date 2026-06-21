"""Sprint R869 — FODG compound analytics deepening tests (Sprint 316)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_149_times_49_plus_shape_times_5600_plus_text_times_5200_plus_page_times_3500,
    fodg_file_size_times_30_plus_shape_times_8_plus_text_times_7_plus_page_times_8,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod149Times49PlusShapeTimes5600PlusTextTimes5200PlusPageTimes3500:
    def test_returns_int(self):
        result = fodg_file_size_mod_149_times_49_plus_shape_times_5600_plus_text_times_5200_plus_page_times_3500(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_149_times_49_plus_shape_times_5600_plus_text_times_5200_plus_page_times_3500(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_149_times_49_plus_shape_times_5600_plus_text_times_5200_plus_page_times_3500(_FODG)
        assert result == 3990

    def test_string_path(self):
        result = fodg_file_size_mod_149_times_49_plus_shape_times_5600_plus_text_times_5200_plus_page_times_3500(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_149_times_49_plus_shape_times_5600_plus_text_times_5200_plus_page_times_3500(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes30PlusShapeTimes8PlusTextTimes7PlusPageTimes8:
    def test_returns_int(self):
        result = fodg_file_size_times_30_plus_shape_times_8_plus_text_times_7_plus_page_times_8(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_30_plus_shape_times_8_plus_text_times_7_plus_page_times_8(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_30_plus_shape_times_8_plus_text_times_7_plus_page_times_8(_FODG)
        assert result == 31598

    def test_string_path(self):
        result = fodg_file_size_times_30_plus_shape_times_8_plus_text_times_7_plus_page_times_8(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_30_plus_shape_times_8_plus_text_times_7_plus_page_times_8(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
