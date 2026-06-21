"""Sprint R830 — FODG compound analytics deepening tests (Sprint 277)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_67_times_21_plus_shape_times_3000_plus_text_times_2600_plus_page_times_1500,
    fodg_file_size_times_16_plus_shape_times_12_plus_text_times_10_plus_page_times_6,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod67Times21PlusShapeTimes3000PlusTextTimes2600PlusPageTimes1500:
    def test_returns_int(self):
        result = fodg_file_size_mod_67_times_21_plus_shape_times_3000_plus_text_times_2600_plus_page_times_1500(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_67_times_21_plus_shape_times_3000_plus_text_times_2600_plus_page_times_1500(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_67_times_21_plus_shape_times_3000_plus_text_times_2600_plus_page_times_1500(_FODG)
        assert result == 2508

    def test_string_path(self):
        result = fodg_file_size_mod_67_times_21_plus_shape_times_3000_plus_text_times_2600_plus_page_times_1500(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_67_times_21_plus_shape_times_3000_plus_text_times_2600_plus_page_times_1500(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes16PlusShapeTimes12PlusTextTimes10PlusPageTimes6:
    def test_returns_int(self):
        result = fodg_file_size_times_16_plus_shape_times_12_plus_text_times_10_plus_page_times_6(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_16_plus_shape_times_12_plus_text_times_10_plus_page_times_6(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_16_plus_shape_times_12_plus_text_times_10_plus_page_times_6(_FODG)
        assert result == 16854

    def test_string_path(self):
        result = fodg_file_size_times_16_plus_shape_times_12_plus_text_times_10_plus_page_times_6(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_16_plus_shape_times_12_plus_text_times_10_plus_page_times_6(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
