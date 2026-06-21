"""Sprint R863 — FODG compound analytics deepening tests (Sprint 310)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_131_times_45_plus_shape_times_5200_plus_text_times_4800_plus_page_times_3100,
    fodg_file_size_times_28_plus_shape_times_6_plus_text_times_5_plus_page_times_6,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod131Times45PlusShapeTimes5200PlusTextTimes4800PlusPageTimes3100:
    def test_returns_int(self):
        result = fodg_file_size_mod_131_times_45_plus_shape_times_5200_plus_text_times_4800_plus_page_times_3100(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_131_times_45_plus_shape_times_5200_plus_text_times_4800_plus_page_times_3100(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_131_times_45_plus_shape_times_5200_plus_text_times_4800_plus_page_times_3100(_FODG)
        assert result == 3325

    def test_string_path(self):
        result = fodg_file_size_mod_131_times_45_plus_shape_times_5200_plus_text_times_4800_plus_page_times_3100(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_131_times_45_plus_shape_times_5200_plus_text_times_4800_plus_page_times_3100(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes28PlusShapeTimes6PlusTextTimes5PlusPageTimes6:
    def test_returns_int(self):
        result = fodg_file_size_times_28_plus_shape_times_6_plus_text_times_5_plus_page_times_6(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_28_plus_shape_times_6_plus_text_times_5_plus_page_times_6(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_28_plus_shape_times_6_plus_text_times_5_plus_page_times_6(_FODG)
        assert result == 29490

    def test_string_path(self):
        result = fodg_file_size_times_28_plus_shape_times_6_plus_text_times_5_plus_page_times_6(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_28_plus_shape_times_6_plus_text_times_5_plus_page_times_6(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
