"""Sprint R845 — FODG compound analytics deepening tests (Sprint 292)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_97_times_31_plus_shape_times_4000_plus_text_times_3600_plus_page_times_2000,
    fodg_file_size_times_22_plus_shape_times_2_plus_text_times_1_plus_page_times_1,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod97Times31PlusShapeTimes4000PlusTextTimes3600PlusPageTimes2000:
    def test_returns_int(self):
        result = fodg_file_size_mod_97_times_31_plus_shape_times_4000_plus_text_times_3600_plus_page_times_2000(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_97_times_31_plus_shape_times_4000_plus_text_times_3600_plus_page_times_2000(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_97_times_31_plus_shape_times_4000_plus_text_times_3600_plus_page_times_2000(_FODG)
        assert result == 4573

    def test_string_path(self):
        result = fodg_file_size_mod_97_times_31_plus_shape_times_4000_plus_text_times_3600_plus_page_times_2000(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_97_times_31_plus_shape_times_4000_plus_text_times_3600_plus_page_times_2000(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes22PlusShapeTimes2PlusTextTimes1PlusPageTimes1:
    def test_returns_int(self):
        result = fodg_file_size_times_22_plus_shape_times_2_plus_text_times_1_plus_page_times_1(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_22_plus_shape_times_2_plus_text_times_1_plus_page_times_1(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_22_plus_shape_times_2_plus_text_times_1_plus_page_times_1(_FODG)
        assert result == 23167

    def test_string_path(self):
        result = fodg_file_size_times_22_plus_shape_times_2_plus_text_times_1_plus_page_times_1(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_22_plus_shape_times_2_plus_text_times_1_plus_page_times_1(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
