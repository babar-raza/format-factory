"""Sprint 205 FODG deepening — 2 new analytics functions, 12 tests.

Functions:
  fodg_file_size_plus_shape_count_plus_text_count_squared
  fodg_file_size_div_100_plus_shape_count_times_text_count_plus_1

Samples (samples/by-format/fodg/):
  empty-page.fodg      sz=1053, sc=0, tc=0
  minimal-drawing.fodg sz=1473, sc=1, tc=1
  shapes-basic.fodg    sz=1628, sc=3, tc=2

Expected:
  fodg_file_size_plus_shape_count_plus_text_count_squared:
    empty   = 1053 + (0+0)^2 = 1053
    minimal = 1473 + (1+1)^2 = 1477
    shapes  = 1628 + (3+2)^2 = 1653

  fodg_file_size_div_100_plus_shape_count_times_text_count_plus_1:
    empty   = 1053//100 + 0*0 + 1 = 11
    minimal = 1473//100 + 1*1 + 1 = 16
    shapes  = 1628//100 + 3*2 + 1 = 23
"""
from pathlib import Path

import pytest

from src.python.fodg import (
    fodg_file_size_plus_shape_count_plus_text_count_squared,
    fodg_file_size_div_100_plus_shape_count_times_text_count_plus_1,
)

_FODG = Path("samples/by-format/fodg")
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"


class TestFodgFileSizePlusShapeCountPlusTextCountSquared:
    def test_empty_value(self):
        assert fodg_file_size_plus_shape_count_plus_text_count_squared(EMPTY) == 1053

    def test_minimal_value(self):
        assert fodg_file_size_plus_shape_count_plus_text_count_squared(MINIMAL) == 1477

    def test_shapes_value(self):
        assert fodg_file_size_plus_shape_count_plus_text_count_squared(SHAPES) == 1653

    def test_returns_int(self):
        assert isinstance(fodg_file_size_plus_shape_count_plus_text_count_squared(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_plus_shape_count_plus_text_count_squared(EMPTY),
            fodg_file_size_plus_shape_count_plus_text_count_squared(MINIMAL),
            fodg_file_size_plus_shape_count_plus_text_count_squared(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_plus_shape_count_plus_text_count_squared(EMPTY) > 0


class TestFodgFileSizeDiv100PlusShapeCountTimesTextCountPlus1:
    def test_empty_value(self):
        assert fodg_file_size_div_100_plus_shape_count_times_text_count_plus_1(EMPTY) == 11

    def test_minimal_value(self):
        assert fodg_file_size_div_100_plus_shape_count_times_text_count_plus_1(MINIMAL) == 16

    def test_shapes_value(self):
        assert fodg_file_size_div_100_plus_shape_count_times_text_count_plus_1(SHAPES) == 23

    def test_returns_int(self):
        assert isinstance(fodg_file_size_div_100_plus_shape_count_times_text_count_plus_1(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_div_100_plus_shape_count_times_text_count_plus_1(EMPTY),
            fodg_file_size_div_100_plus_shape_count_times_text_count_plus_1(MINIMAL),
            fodg_file_size_div_100_plus_shape_count_times_text_count_plus_1(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_div_100_plus_shape_count_times_text_count_plus_1(EMPTY) > 0
