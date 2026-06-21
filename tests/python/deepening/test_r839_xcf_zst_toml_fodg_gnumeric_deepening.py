"""Sprint R839 — FODG compound analytics deepening tests (Sprint 286)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_83_times_27_plus_shape_times_3600_plus_text_times_3200_plus_page_times_1800,
    fodg_file_size_times_20_plus_shape_times_4_plus_text_times_3_plus_page_times_1,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod83Times27PlusShapeTimes3600PlusTextTimes3200PlusPageTimes1800:
    def test_returns_int(self):
        result = fodg_file_size_mod_83_times_27_plus_shape_times_3600_plus_text_times_3200_plus_page_times_1800(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_83_times_27_plus_shape_times_3600_plus_text_times_3200_plus_page_times_1800(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_83_times_27_plus_shape_times_3600_plus_text_times_3200_plus_page_times_1800(_FODG)
        assert result == 3339

    def test_string_path(self):
        result = fodg_file_size_mod_83_times_27_plus_shape_times_3600_plus_text_times_3200_plus_page_times_1800(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_83_times_27_plus_shape_times_3600_plus_text_times_3200_plus_page_times_1800(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes20PlusShapeTimes4PlusTextTimes3PlusPageTimes1:
    def test_returns_int(self):
        result = fodg_file_size_times_20_plus_shape_times_4_plus_text_times_3_plus_page_times_1(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_20_plus_shape_times_4_plus_text_times_3_plus_page_times_1(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_20_plus_shape_times_4_plus_text_times_3_plus_page_times_1(_FODG)
        assert result == 21061

    def test_string_path(self):
        result = fodg_file_size_times_20_plus_shape_times_4_plus_text_times_3_plus_page_times_1(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_20_plus_shape_times_4_plus_text_times_3_plus_page_times_1(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
