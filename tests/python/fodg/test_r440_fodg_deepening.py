"""Sprint 211 FODG deepening — 2 new analytics functions, 12 tests.

Functions:
  fodg_file_size_div_20_plus_shape_count_times_50_plus_text_count
  fodg_file_size_plus_text_count_times_shape_count_times_1000

Samples (samples/by-format/fodg/):
  empty-page.fodg      sz=1053, sc=0, tc=0
  minimal-drawing.fodg sz=1473, sc=1, tc=1
  shapes-basic.fodg    sz=1628, sc=3, tc=2

Expected:
  fodg_file_size_div_20_plus_shape_count_times_50_plus_text_count:
    empty   = 1053//20 + 0*50 + 0  = 52
    minimal = 1473//20 + 1*50 + 1  = 124
    shapes  = 1628//20 + 3*50 + 2  = 233

  fodg_file_size_plus_text_count_times_shape_count_times_1000:
    empty   = 1053 + 0*0*1000 = 1053
    minimal = 1473 + 1*1*1000 = 2473
    shapes  = 1628 + 2*3*1000 = 7628
"""
from pathlib import Path

import pytest

from src.python.fodg import (
    fodg_file_size_div_20_plus_shape_count_times_50_plus_text_count,
    fodg_file_size_plus_text_count_times_shape_count_times_1000,
)

_FODG = Path("samples/by-format/fodg")
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"


class TestFodgFileSizeDiv20PlusShapeCountTimes50PlusTextCount:
    def test_empty_value(self):
        assert fodg_file_size_div_20_plus_shape_count_times_50_plus_text_count(EMPTY) == 52

    def test_minimal_value(self):
        assert fodg_file_size_div_20_plus_shape_count_times_50_plus_text_count(MINIMAL) == 124

    def test_shapes_value(self):
        assert fodg_file_size_div_20_plus_shape_count_times_50_plus_text_count(SHAPES) == 233

    def test_returns_int(self):
        assert isinstance(fodg_file_size_div_20_plus_shape_count_times_50_plus_text_count(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_div_20_plus_shape_count_times_50_plus_text_count(EMPTY),
            fodg_file_size_div_20_plus_shape_count_times_50_plus_text_count(MINIMAL),
            fodg_file_size_div_20_plus_shape_count_times_50_plus_text_count(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_div_20_plus_shape_count_times_50_plus_text_count(EMPTY) > 0


class TestFodgFileSizePlusTextCountTimesShapeCountTimes1000:
    def test_empty_value(self):
        assert fodg_file_size_plus_text_count_times_shape_count_times_1000(EMPTY) == 1053

    def test_minimal_value(self):
        assert fodg_file_size_plus_text_count_times_shape_count_times_1000(MINIMAL) == 2473

    def test_shapes_value(self):
        assert fodg_file_size_plus_text_count_times_shape_count_times_1000(SHAPES) == 7628

    def test_returns_int(self):
        assert isinstance(fodg_file_size_plus_text_count_times_shape_count_times_1000(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_plus_text_count_times_shape_count_times_1000(EMPTY),
            fodg_file_size_plus_text_count_times_shape_count_times_1000(MINIMAL),
            fodg_file_size_plus_text_count_times_shape_count_times_1000(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_plus_text_count_times_shape_count_times_1000(EMPTY) > 0
