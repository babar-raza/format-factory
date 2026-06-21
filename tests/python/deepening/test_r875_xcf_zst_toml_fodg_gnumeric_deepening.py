"""Sprint R875 — FODG compound analytics deepening tests (Sprint 322)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_157_times_53_plus_shape_times_6000_plus_text_times_5600_plus_page_times_3900,
    fodg_file_size_times_34_plus_shape_times_10_plus_text_times_9_plus_page_times_10,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod157Times53PlusShapeTimes6000PlusTextTimes5600PlusPageTimes3900:
    def test_returns_int(self):
        result = fodg_file_size_mod_157_times_53_plus_shape_times_6000_plus_text_times_5600_plus_page_times_3900(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_157_times_53_plus_shape_times_6000_plus_text_times_5600_plus_page_times_3900(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_157_times_53_plus_shape_times_6000_plus_text_times_5600_plus_page_times_3900(_FODG)
        assert result == 9783

    def test_string_path(self):
        result = fodg_file_size_mod_157_times_53_plus_shape_times_6000_plus_text_times_5600_plus_page_times_3900(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_157_times_53_plus_shape_times_6000_plus_text_times_5600_plus_page_times_3900(
            SAMPLES / "fodg" / "empty-page.fodg"
        )
        assert isinstance(result, int)


class TestFodgFileSizeTimes34PlusShapeTimes10PlusTextTimes9PlusPageTimes10:
    def test_returns_int(self):
        result = fodg_file_size_times_34_plus_shape_times_10_plus_text_times_9_plus_page_times_10(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_34_plus_shape_times_10_plus_text_times_9_plus_page_times_10(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_34_plus_shape_times_10_plus_text_times_9_plus_page_times_10(_FODG)
        assert result == 35812

    def test_string_path(self):
        result = fodg_file_size_times_34_plus_shape_times_10_plus_text_times_9_plus_page_times_10(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_34_plus_shape_times_10_plus_text_times_9_plus_page_times_10(
            SAMPLES / "fodg" / "empty-page.fodg"
        )
        assert isinstance(result, int)
