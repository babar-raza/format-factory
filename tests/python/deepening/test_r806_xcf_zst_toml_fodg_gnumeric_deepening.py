"""Sprint R806 — FODG compound analytics deepening tests (Sprint 253)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_29_times_5_plus_shape_times_1600_plus_text_times_1200_plus_page_times_700,
    fodg_file_size_times_8_plus_shape_times_500_plus_text_times_250_plus_page_times_150,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod29Times5PlusShapeTimes1600PlusTextTimes1200PlusPageTimes700:
    def test_returns_int(self):
        result = fodg_file_size_mod_29_times_5_plus_shape_times_1600_plus_text_times_1200_plus_page_times_700(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_29_times_5_plus_shape_times_1600_plus_text_times_1200_plus_page_times_700(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_29_times_5_plus_shape_times_1600_plus_text_times_1200_plus_page_times_700(_FODG)
        assert result == 745

    def test_string_path(self):
        result = fodg_file_size_mod_29_times_5_plus_shape_times_1600_plus_text_times_1200_plus_page_times_700(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_29_times_5_plus_shape_times_1600_plus_text_times_1200_plus_page_times_700(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes8PlusShapeTimes500PlusTextTimes250PlusPageTimes150:
    def test_returns_int(self):
        result = fodg_file_size_times_8_plus_shape_times_500_plus_text_times_250_plus_page_times_150(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_8_plus_shape_times_500_plus_text_times_250_plus_page_times_150(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_8_plus_shape_times_500_plus_text_times_250_plus_page_times_150(_FODG)
        assert result == 8574

    def test_string_path(self):
        result = fodg_file_size_times_8_plus_shape_times_500_plus_text_times_250_plus_page_times_150(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_8_plus_shape_times_500_plus_text_times_250_plus_page_times_150(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
