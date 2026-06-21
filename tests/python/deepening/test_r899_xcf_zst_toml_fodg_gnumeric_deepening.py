"""Sprint R899 — FODG compound analytics deepening tests (Sprint 346)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_211_times_73_plus_shape_times_8200_plus_text_times_7800_plus_page_times_6100,
    fodg_file_size_times_53_plus_shape_times_21_plus_text_times_20_plus_page_times_21,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod211Times73PlusShapeTimes8200PlusTextTimes7800PlusPageTimes6100:
    def test_returns_int(self):
        result = fodg_file_size_mod_211_times_73_plus_shape_times_8200_plus_text_times_7800_plus_page_times_6100(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_211_times_73_plus_shape_times_8200_plus_text_times_7800_plus_page_times_6100(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_211_times_73_plus_shape_times_8200_plus_text_times_7800_plus_page_times_6100(_FODG)
        assert result == 21357

    def test_string_path(self):
        result = fodg_file_size_mod_211_times_73_plus_shape_times_8200_plus_text_times_7800_plus_page_times_6100(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_211_times_73_plus_shape_times_8200_plus_text_times_7800_plus_page_times_6100(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes53PlusShapeTimes21PlusTextTimes20PlusPageTimes21:
    def test_returns_int(self):
        result = fodg_file_size_times_53_plus_shape_times_21_plus_text_times_20_plus_page_times_21(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_53_plus_shape_times_21_plus_text_times_20_plus_page_times_21(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_53_plus_shape_times_21_plus_text_times_20_plus_page_times_21(_FODG)
        assert result == 55830

    def test_string_path(self):
        result = fodg_file_size_times_53_plus_shape_times_21_plus_text_times_20_plus_page_times_21(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_53_plus_shape_times_21_plus_text_times_20_plus_page_times_21(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
