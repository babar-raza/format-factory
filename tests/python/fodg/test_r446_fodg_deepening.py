"""Sprint 217 FODG deepening — 2 new analytics functions, 12 tests.

Functions:
  fodg_file_size_div_10_plus_shape_count_squared_times_100_plus_text_count
  fodg_file_size_times_text_count_plus_1_div_50

Samples (samples/by-format/fodg/):
  empty-page.fodg      sz=1053, sc=0, tc=0
  minimal-drawing.fodg sz=1473, sc=1, tc=1
  shapes-basic.fodg    sz=1628, sc=3, tc=2

Expected:
  fodg_file_size_div_10_plus_shape_count_squared_times_100_plus_text_count:
    empty   = 1053//10 + 0**2*100 + 0  = 105
    minimal = 1473//10 + 1**2*100 + 1  = 248
    shapes  = 1628//10 + 3**2*100 + 2  = 1064

  fodg_file_size_times_text_count_plus_1_div_50:
    empty   = 1053*(0+1)//50 = 21
    minimal = 1473*(1+1)//50 = 58
    shapes  = 1628*(2+1)//50 = 97
"""
from pathlib import Path

import pytest

from src.python.fodg import (
    fodg_file_size_div_10_plus_shape_count_squared_times_100_plus_text_count,
    fodg_file_size_times_text_count_plus_1_div_50,
)

_FODG = Path("samples/by-format/fodg")
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"


class TestFodgFileSizeDiv10PlusShapeCountSquaredTimes100PlusTextCount:
    def test_empty_value(self):
        assert fodg_file_size_div_10_plus_shape_count_squared_times_100_plus_text_count(EMPTY) == 105

    def test_minimal_value(self):
        assert fodg_file_size_div_10_plus_shape_count_squared_times_100_plus_text_count(MINIMAL) == 248

    def test_shapes_value(self):
        assert fodg_file_size_div_10_plus_shape_count_squared_times_100_plus_text_count(SHAPES) == 1064

    def test_returns_int(self):
        assert isinstance(fodg_file_size_div_10_plus_shape_count_squared_times_100_plus_text_count(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_div_10_plus_shape_count_squared_times_100_plus_text_count(EMPTY),
            fodg_file_size_div_10_plus_shape_count_squared_times_100_plus_text_count(MINIMAL),
            fodg_file_size_div_10_plus_shape_count_squared_times_100_plus_text_count(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_div_10_plus_shape_count_squared_times_100_plus_text_count(EMPTY) > 0


class TestFodgFileSizeTimesTextCountPlus1Div50:
    def test_empty_value(self):
        assert fodg_file_size_times_text_count_plus_1_div_50(EMPTY) == 21

    def test_minimal_value(self):
        assert fodg_file_size_times_text_count_plus_1_div_50(MINIMAL) == 58

    def test_shapes_value(self):
        assert fodg_file_size_times_text_count_plus_1_div_50(SHAPES) == 97

    def test_returns_int(self):
        assert isinstance(fodg_file_size_times_text_count_plus_1_div_50(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_times_text_count_plus_1_div_50(EMPTY),
            fodg_file_size_times_text_count_plus_1_div_50(MINIMAL),
            fodg_file_size_times_text_count_plus_1_div_50(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_times_text_count_plus_1_div_50(EMPTY) > 0
