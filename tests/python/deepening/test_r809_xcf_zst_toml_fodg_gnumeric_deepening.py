"""Sprint R809 — FODG compound analytics deepening tests (Sprint 256)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_37_times_7_plus_shape_times_1700_plus_text_times_1300_plus_page_times_800,
    fodg_file_size_times_9_plus_shape_times_400_plus_text_times_200_plus_page_times_100,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod37Times7PlusShapeTimes1700PlusTextTimes1300PlusPageTimes800:
    def test_returns_int(self):
        result = fodg_file_size_mod_37_times_7_plus_shape_times_1700_plus_text_times_1300_plus_page_times_800(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_37_times_7_plus_shape_times_1700_plus_text_times_1300_plus_page_times_800(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_37_times_7_plus_shape_times_1700_plus_text_times_1300_plus_page_times_800(_FODG)
        assert result == 919

    def test_string_path(self):
        result = fodg_file_size_mod_37_times_7_plus_shape_times_1700_plus_text_times_1300_plus_page_times_800(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_37_times_7_plus_shape_times_1700_plus_text_times_1300_plus_page_times_800(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)


class TestFodgFileSizeTimes9PlusShapeTimes400PlusTextTimes200PlusPageTimes100:
    def test_returns_int(self):
        result = fodg_file_size_times_9_plus_shape_times_400_plus_text_times_200_plus_page_times_100(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_9_plus_shape_times_400_plus_text_times_200_plus_page_times_100(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_9_plus_shape_times_400_plus_text_times_200_plus_page_times_100(_FODG)
        assert result == 9577

    def test_string_path(self):
        result = fodg_file_size_times_9_plus_shape_times_400_plus_text_times_200_plus_page_times_100(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_9_plus_shape_times_400_plus_text_times_200_plus_page_times_100(SAMPLES / "fodg" / "empty-page.fodg")
        assert isinstance(result, int)
