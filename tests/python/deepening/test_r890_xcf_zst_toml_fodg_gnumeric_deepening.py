"""Sprint R890 — FODG compound analytics deepening tests (Sprint 337)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_193_times_67_plus_shape_times_7600_plus_text_times_7200_plus_page_times_5500,
    fodg_file_size_times_47_plus_shape_times_18_plus_text_times_17_plus_page_times_18,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod193Times67PlusShapeTimes7600PlusTextTimes7200PlusPageTimes5500:
    def test_returns_int(self):
        result = fodg_file_size_mod_193_times_67_plus_shape_times_7600_plus_text_times_7200_plus_page_times_5500(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_193_times_67_plus_shape_times_7600_plus_text_times_7200_plus_page_times_5500(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_193_times_67_plus_shape_times_7600_plus_text_times_7200_plus_page_times_5500(_FODG)
        assert result == 11396

    def test_string_path(self):
        result = fodg_file_size_mod_193_times_67_plus_shape_times_7600_plus_text_times_7200_plus_page_times_5500(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_193_times_67_plus_shape_times_7600_plus_text_times_7200_plus_page_times_5500(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes47PlusShapeTimes18PlusTextTimes17PlusPageTimes18:
    def test_returns_int(self):
        result = fodg_file_size_times_47_plus_shape_times_18_plus_text_times_17_plus_page_times_18(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_47_plus_shape_times_18_plus_text_times_17_plus_page_times_18(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_47_plus_shape_times_18_plus_text_times_17_plus_page_times_18(_FODG)
        assert result == 49509

    def test_string_path(self):
        result = fodg_file_size_times_47_plus_shape_times_18_plus_text_times_17_plus_page_times_18(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_47_plus_shape_times_18_plus_text_times_17_plus_page_times_18(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
