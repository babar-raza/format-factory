"""Sprint 214 FODG deepening — 2 new analytics functions, 12 tests.

Functions:
  fodg_file_size_times_shape_count_plus_1_div_100
  fodg_file_size_mod_200_plus_shape_count_times_100

Samples (samples/by-format/fodg/):
  empty-page.fodg      sz=1053, sc=0, tc=0
  minimal-drawing.fodg sz=1473, sc=1, tc=1
  shapes-basic.fodg    sz=1628, sc=3, tc=2

Expected:
  fodg_file_size_times_shape_count_plus_1_div_100:
    empty   = 1053*(0+1)//100 = 10
    minimal = 1473*(1+1)//100 = 29
    shapes  = 1628*(3+1)//100 = 65

  fodg_file_size_mod_200_plus_shape_count_times_100:
    empty   = 1053%200 + 0*100 = 53
    minimal = 1473%200 + 1*100 = 173
    shapes  = 1628%200 + 3*100 = 328
"""
from pathlib import Path

import pytest

from src.python.fodg import (
    fodg_file_size_times_shape_count_plus_1_div_100,
    fodg_file_size_mod_200_plus_shape_count_times_100,
)

_FODG = Path("samples/by-format/fodg")
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"


class TestFodgFileSizeTimesShapeCountPlus1Div100:
    def test_empty_value(self):
        assert fodg_file_size_times_shape_count_plus_1_div_100(EMPTY) == 10

    def test_minimal_value(self):
        assert fodg_file_size_times_shape_count_plus_1_div_100(MINIMAL) == 29

    def test_shapes_value(self):
        assert fodg_file_size_times_shape_count_plus_1_div_100(SHAPES) == 65

    def test_returns_int(self):
        assert isinstance(fodg_file_size_times_shape_count_plus_1_div_100(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_times_shape_count_plus_1_div_100(EMPTY),
            fodg_file_size_times_shape_count_plus_1_div_100(MINIMAL),
            fodg_file_size_times_shape_count_plus_1_div_100(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_times_shape_count_plus_1_div_100(EMPTY) > 0


class TestFodgFileSizeMod200PlusShapeCountTimes100:
    def test_empty_value(self):
        assert fodg_file_size_mod_200_plus_shape_count_times_100(EMPTY) == 53

    def test_minimal_value(self):
        assert fodg_file_size_mod_200_plus_shape_count_times_100(MINIMAL) == 173

    def test_shapes_value(self):
        assert fodg_file_size_mod_200_plus_shape_count_times_100(SHAPES) == 328

    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_200_plus_shape_count_times_100(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_mod_200_plus_shape_count_times_100(EMPTY),
            fodg_file_size_mod_200_plus_shape_count_times_100(MINIMAL),
            fodg_file_size_mod_200_plus_shape_count_times_100(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_mod_200_plus_shape_count_times_100(EMPTY) > 0
