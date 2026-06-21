"""Sprint 199 FODG deepening — 2 new analytics functions, 12 tests.

Functions:
  fodg_file_size_times_3_div_10_plus_text_count_times_shape_count
  fodg_file_size_plus_shape_count_times_200_plus_text_count

Samples (samples/by-format/fodg/):
  empty-page.fodg      sz=1053, sc=0, tc=0
  minimal-drawing.fodg sz=1473, sc=1, tc=1
  shapes-basic.fodg    sz=1628, sc=3, tc=2

Expected:
  fodg_file_size_times_3_div_10_plus_text_count_times_shape_count:
    empty   = 1053*3//10 + 0*0  = 315
    minimal = 1473*3//10 + 1*1  = 442
    shapes  = 1628*3//10 + 2*3  = 494

  fodg_file_size_plus_shape_count_times_200_plus_text_count:
    empty   = 1053 + 0*200 + 0 = 1053
    minimal = 1473 + 1*200 + 1 = 1674
    shapes  = 1628 + 3*200 + 2 = 2230
"""
from pathlib import Path

import pytest

from src.python.fodg import (
    fodg_file_size_times_3_div_10_plus_text_count_times_shape_count,
    fodg_file_size_plus_shape_count_times_200_plus_text_count,
)

_FODG = Path("samples/by-format/fodg")
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"


class TestFodgFileSizeTimes3Div10PlusTextCountTimesShapeCount:
    def test_empty_value(self):
        assert fodg_file_size_times_3_div_10_plus_text_count_times_shape_count(EMPTY) == 315

    def test_minimal_value(self):
        assert fodg_file_size_times_3_div_10_plus_text_count_times_shape_count(MINIMAL) == 442

    def test_shapes_value(self):
        assert fodg_file_size_times_3_div_10_plus_text_count_times_shape_count(SHAPES) == 494

    def test_returns_int(self):
        assert isinstance(fodg_file_size_times_3_div_10_plus_text_count_times_shape_count(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_times_3_div_10_plus_text_count_times_shape_count(EMPTY),
            fodg_file_size_times_3_div_10_plus_text_count_times_shape_count(MINIMAL),
            fodg_file_size_times_3_div_10_plus_text_count_times_shape_count(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_times_3_div_10_plus_text_count_times_shape_count(EMPTY) > 0


class TestFodgFileSizePlusShapeCountTimes200PlusTextCount:
    def test_empty_value(self):
        assert fodg_file_size_plus_shape_count_times_200_plus_text_count(EMPTY) == 1053

    def test_minimal_value(self):
        assert fodg_file_size_plus_shape_count_times_200_plus_text_count(MINIMAL) == 1674

    def test_shapes_value(self):
        assert fodg_file_size_plus_shape_count_times_200_plus_text_count(SHAPES) == 2230

    def test_returns_int(self):
        assert isinstance(fodg_file_size_plus_shape_count_times_200_plus_text_count(EMPTY), int)

    def test_shapes_largest(self):
        assert fodg_file_size_plus_shape_count_times_200_plus_text_count(SHAPES) > fodg_file_size_plus_shape_count_times_200_plus_text_count(MINIMAL)

    def test_positive(self):
        assert fodg_file_size_plus_shape_count_times_200_plus_text_count(EMPTY) > 0
