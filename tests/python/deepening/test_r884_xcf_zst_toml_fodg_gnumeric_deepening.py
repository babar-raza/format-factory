"""Sprint R884 — FODG compound analytics deepening tests (Sprint 331)."""
import sys
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

import pytest

from src.python.fodg import (
    fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300,
    fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13,
)

SAMPLES = _REPO / "samples" / "by-format"
_FODG = str(SAMPLES / "fodg" / "empty-page.fodg")


class TestFodgFileSizeMod383Times23PlusShapeCountTimes3600PlusTextCountTimes3300:
    def test_returns_int(self):
        result = fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300(_FODG)
        assert result == 6601

    def test_string_path(self):
        result = fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_mod_383_times_23_plus_shape_count_times_3600_plus_text_count_times_3300(
            SAMPLES / "fodg" / "empty-page.fodg"
        )
        assert isinstance(result, int)


class TestFodgFileSizeTimes39PlusShapeTimes13PlusTextTimes12PlusPageTimes13:
    def test_returns_int(self):
        result = fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13(_FODG)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13(_FODG)
        assert result >= 0

    def test_expected_value(self):
        result = fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13(_FODG)
        assert result == 41080

    def test_string_path(self):
        result = fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13(str(_FODG))
        assert isinstance(result, int)

    def test_pathlib_path(self):
        result = fodg_file_size_times_39_plus_shape_times_13_plus_text_times_12_plus_page_times_13(
            SAMPLES / "fodg" / "empty-page.fodg"
        )
        assert isinstance(result, int)
