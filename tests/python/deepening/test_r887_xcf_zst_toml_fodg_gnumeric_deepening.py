"""Sprint R887 — FODG compound analytics deepening tests (Sprint 334)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_187_times_63_plus_shape_times_7200_plus_text_times_6800_plus_page_times_5100,
    fodg_file_size_times_43_plus_shape_times_16_plus_text_times_15_plus_page_times_16,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod187Times63PlusShapeTimes7200PlusTextTimes6800PlusPageTimes5100:
    def test_returns_int(self):
        result = fodg_file_size_mod_187_times_63_plus_shape_times_7200_plus_text_times_6800_plus_page_times_5100(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_187_times_63_plus_shape_times_7200_plus_text_times_6800_plus_page_times_5100(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_187_times_63_plus_shape_times_7200_plus_text_times_6800_plus_page_times_5100(_FODG)
        assert result == 12534

    def test_string_path(self):
        result = fodg_file_size_mod_187_times_63_plus_shape_times_7200_plus_text_times_6800_plus_page_times_5100(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_187_times_63_plus_shape_times_7200_plus_text_times_6800_plus_page_times_5100(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes43PlusShapeTimes16PlusTextTimes15PlusPageTimes16:
    def test_returns_int(self):
        result = fodg_file_size_times_43_plus_shape_times_16_plus_text_times_15_plus_page_times_16(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_43_plus_shape_times_16_plus_text_times_15_plus_page_times_16(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_43_plus_shape_times_16_plus_text_times_15_plus_page_times_16(_FODG)
        assert result == 45295

    def test_string_path(self):
        result = fodg_file_size_times_43_plus_shape_times_16_plus_text_times_15_plus_page_times_16(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_43_plus_shape_times_16_plus_text_times_15_plus_page_times_16(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
