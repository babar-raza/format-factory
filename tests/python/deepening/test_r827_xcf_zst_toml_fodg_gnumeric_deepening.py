"""Sprint R827 — FODG compound analytics deepening tests (Sprint 274)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_61_times_19_plus_shape_times_2800_plus_text_times_2400_plus_page_times_1400,
    fodg_file_size_times_15_plus_shape_times_20_plus_text_times_15_plus_page_times_8,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod61Times19PlusShapeTimes2800PlusTextTimes2400PlusPageTimes1400:
    def test_returns_int(self):
        result = fodg_file_size_mod_61_times_19_plus_shape_times_2800_plus_text_times_2400_plus_page_times_1400(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_61_times_19_plus_shape_times_2800_plus_text_times_2400_plus_page_times_1400(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_61_times_19_plus_shape_times_2800_plus_text_times_2400_plus_page_times_1400(_FODG)
        assert result == 1704

    def test_string_path(self):
        result = fodg_file_size_mod_61_times_19_plus_shape_times_2800_plus_text_times_2400_plus_page_times_1400(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_61_times_19_plus_shape_times_2800_plus_text_times_2400_plus_page_times_1400(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes15PlusShapeTimes20PlusTextTimes15PlusPageTimes8:
    def test_returns_int(self):
        result = fodg_file_size_times_15_plus_shape_times_20_plus_text_times_15_plus_page_times_8(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_15_plus_shape_times_20_plus_text_times_15_plus_page_times_8(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_15_plus_shape_times_20_plus_text_times_15_plus_page_times_8(_FODG)
        assert result == 15803

    def test_string_path(self):
        result = fodg_file_size_times_15_plus_shape_times_20_plus_text_times_15_plus_page_times_8(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_15_plus_shape_times_20_plus_text_times_15_plus_page_times_8(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
