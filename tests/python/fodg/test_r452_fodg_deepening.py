"""Sprint 223 FODG deepening — 2 new analytics functions, 12 tests.

Functions:
  fodg_file_size_div_shape_count_plus_text_count_plus_1
  fodg_file_size_times_3_plus_shape_count_times_500_minus_text_count_times_200

Samples (samples/by-format/fodg/):
  empty-page.fodg      sz=1053, sc=0, tc=0
  minimal-drawing.fodg sz=1473, sc=1, tc=1
  shapes-basic.fodg    sz=1628, sc=3, tc=2

Expected:
  fodg_file_size_div_shape_count_plus_text_count_plus_1:
    empty   = 1053 // (0+0+1) = 1053
    minimal = 1473 // (1+1+1) = 491
    shapes  = 1628 // (3+2+1) = 271

  fodg_file_size_times_3_plus_shape_count_times_500_minus_text_count_times_200:
    empty   = 1053*3 + 0*500 - 0*200   = 3159
    minimal = 1473*3 + 1*500 - 1*200   = 4719
    shapes  = 1628*3 + 3*500 - 2*200   = 5984
"""
from pathlib import Path

import pytest

from src.python.fodg import (
    fodg_file_size_div_shape_count_plus_text_count_plus_1,
    fodg_file_size_times_3_plus_shape_count_times_500_minus_text_count_times_200,
)

_FODG = Path("samples/by-format/fodg")
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"


class TestFodgFileSizeDivShapeCountPlusTextCountPlus1:
    def test_empty_value(self):
        assert fodg_file_size_div_shape_count_plus_text_count_plus_1(EMPTY) == 1053

    def test_minimal_value(self):
        assert fodg_file_size_div_shape_count_plus_text_count_plus_1(MINIMAL) == 491

    def test_shapes_value(self):
        assert fodg_file_size_div_shape_count_plus_text_count_plus_1(SHAPES) == 271

    def test_returns_int(self):
        assert isinstance(fodg_file_size_div_shape_count_plus_text_count_plus_1(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_div_shape_count_plus_text_count_plus_1(EMPTY),
            fodg_file_size_div_shape_count_plus_text_count_plus_1(MINIMAL),
            fodg_file_size_div_shape_count_plus_text_count_plus_1(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_div_shape_count_plus_text_count_plus_1(EMPTY) > 0


class TestFodgFileSizeTimes3PlusShapeCountTimes500MinusTextCountTimes200:
    def test_empty_value(self):
        assert fodg_file_size_times_3_plus_shape_count_times_500_minus_text_count_times_200(EMPTY) == 3159

    def test_minimal_value(self):
        assert fodg_file_size_times_3_plus_shape_count_times_500_minus_text_count_times_200(MINIMAL) == 4719

    def test_shapes_value(self):
        assert fodg_file_size_times_3_plus_shape_count_times_500_minus_text_count_times_200(SHAPES) == 5984

    def test_returns_int(self):
        assert isinstance(fodg_file_size_times_3_plus_shape_count_times_500_minus_text_count_times_200(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_times_3_plus_shape_count_times_500_minus_text_count_times_200(EMPTY),
            fodg_file_size_times_3_plus_shape_count_times_500_minus_text_count_times_200(MINIMAL),
            fodg_file_size_times_3_plus_shape_count_times_500_minus_text_count_times_200(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_times_3_plus_shape_count_times_500_minus_text_count_times_200(EMPTY) > 0
