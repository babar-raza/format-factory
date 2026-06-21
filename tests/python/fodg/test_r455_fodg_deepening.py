"""Sprint 226 FODG deepening — 2 new analytics functions, 12 tests.

Functions:
  fodg_file_size_mod_100_plus_shape_count_times_300_plus_text_count_times_150
  fodg_file_size_plus_shape_count_times_text_count_div_100

Samples (samples/by-format/fodg/):
  empty-page.fodg      sz=1053, sc=0, tc=0
  minimal-drawing.fodg sz=1473, sc=1, tc=1
  shapes-basic.fodg    sz=1628, sc=3, tc=2

Expected:
  fodg_file_size_mod_100_plus_shape_count_times_300_plus_text_count_times_150:
    empty   = 1053%100 + 0*300 + 0*150   = 53
    minimal = 1473%100 + 1*300 + 1*150   = 523
    shapes  = 1628%100 + 3*300 + 2*150   = 1228

  fodg_file_size_plus_shape_count_times_text_count_div_100:
    empty   = (1053 + 0*0) // 100  = 10
    minimal = (1473 + 1*1) // 100  = 14
    shapes  = (1628 + 3*2) // 100  = 16
"""
from pathlib import Path

import pytest

from src.python.fodg import (
    fodg_file_size_mod_100_plus_shape_count_times_300_plus_text_count_times_150,
    fodg_file_size_plus_shape_count_times_text_count_div_100,
)

_FODG = Path("samples/by-format/fodg")
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"


class TestFodgFileSizeMod100PlusShapeCountTimes300PlusTextCountTimes150:
    def test_empty_value(self):
        assert fodg_file_size_mod_100_plus_shape_count_times_300_plus_text_count_times_150(EMPTY) == 53

    def test_minimal_value(self):
        assert fodg_file_size_mod_100_plus_shape_count_times_300_plus_text_count_times_150(MINIMAL) == 523

    def test_shapes_value(self):
        assert fodg_file_size_mod_100_plus_shape_count_times_300_plus_text_count_times_150(SHAPES) == 1228

    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_100_plus_shape_count_times_300_plus_text_count_times_150(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_mod_100_plus_shape_count_times_300_plus_text_count_times_150(EMPTY),
            fodg_file_size_mod_100_plus_shape_count_times_300_plus_text_count_times_150(MINIMAL),
            fodg_file_size_mod_100_plus_shape_count_times_300_plus_text_count_times_150(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_mod_100_plus_shape_count_times_300_plus_text_count_times_150(EMPTY) > 0


class TestFodgFileSizePlusShapeCountTimesTextCountDiv100:
    def test_empty_value(self):
        assert fodg_file_size_plus_shape_count_times_text_count_div_100(EMPTY) == 10

    def test_minimal_value(self):
        assert fodg_file_size_plus_shape_count_times_text_count_div_100(MINIMAL) == 14

    def test_shapes_value(self):
        assert fodg_file_size_plus_shape_count_times_text_count_div_100(SHAPES) == 16

    def test_returns_int(self):
        assert isinstance(fodg_file_size_plus_shape_count_times_text_count_div_100(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_plus_shape_count_times_text_count_div_100(EMPTY),
            fodg_file_size_plus_shape_count_times_text_count_div_100(MINIMAL),
            fodg_file_size_plus_shape_count_times_text_count_div_100(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_plus_shape_count_times_text_count_div_100(EMPTY) > 0
