"""Sprint R872 — FODG compound analytics deepening tests (Sprint 319)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_153_times_51_plus_shape_times_5800_plus_text_times_5400_plus_page_times_3700,
    fodg_file_size_times_32_plus_shape_times_9_plus_text_times_8_plus_page_times_9,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod153Times51PlusShapeTimes5800PlusTextTimes5400PlusPageTimes3700:
    def test_returns_int(self):
        result = fodg_file_size_mod_153_times_51_plus_shape_times_5800_plus_text_times_5400_plus_page_times_3700(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_153_times_51_plus_shape_times_5800_plus_text_times_5400_plus_page_times_3700(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_153_times_51_plus_shape_times_5800_plus_text_times_5400_plus_page_times_3700(_FODG)
        assert result == 10585

    def test_string_path(self):
        result = fodg_file_size_mod_153_times_51_plus_shape_times_5800_plus_text_times_5400_plus_page_times_3700(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_153_times_51_plus_shape_times_5800_plus_text_times_5400_plus_page_times_3700(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes32PlusShapeTimes9PlusTextTimes8PlusPageTimes9:
    def test_returns_int(self):
        result = fodg_file_size_times_32_plus_shape_times_9_plus_text_times_8_plus_page_times_9(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_32_plus_shape_times_9_plus_text_times_8_plus_page_times_9(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_32_plus_shape_times_9_plus_text_times_8_plus_page_times_9(_FODG)
        assert result == 33705

    def test_string_path(self):
        result = fodg_file_size_times_32_plus_shape_times_9_plus_text_times_8_plus_page_times_9(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_32_plus_shape_times_9_plus_text_times_8_plus_page_times_9(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
