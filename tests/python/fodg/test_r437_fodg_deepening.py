"""Sprint 208 FODG deepening — 2 new analytics functions, 12 tests.

Functions:
  fodg_file_size_mod_500_plus_shape_count_plus_text_count
  fodg_file_size_div_50_times_shape_count_plus_1

Samples (samples/by-format/fodg/):
  empty-page.fodg      sz=1053, sc=0, tc=0
  minimal-drawing.fodg sz=1473, sc=1, tc=1
  shapes-basic.fodg    sz=1628, sc=3, tc=2

Expected:
  fodg_file_size_mod_500_plus_shape_count_plus_text_count:
    empty   = 1053%500 + 0 + 0 = 53
    minimal = 1473%500 + 1 + 1 = 475
    shapes  = 1628%500 + 3 + 2 = 133

  fodg_file_size_div_50_times_shape_count_plus_1:
    empty   = 1053//50 * (0+1) = 21
    minimal = 1473//50 * (1+1) = 58
    shapes  = 1628//50 * (3+1) = 128
"""
from pathlib import Path

import pytest

from src.python.fodg import (
    fodg_file_size_mod_500_plus_shape_count_plus_text_count,
    fodg_file_size_div_50_times_shape_count_plus_1,
)

_FODG = Path("samples/by-format/fodg")
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"


class TestFodgFileSizeMod500PlusShapeCountPlusTextCount:
    def test_empty_value(self):
        assert fodg_file_size_mod_500_plus_shape_count_plus_text_count(EMPTY) == 53

    def test_minimal_value(self):
        assert fodg_file_size_mod_500_plus_shape_count_plus_text_count(MINIMAL) == 475

    def test_shapes_value(self):
        assert fodg_file_size_mod_500_plus_shape_count_plus_text_count(SHAPES) == 133

    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_500_plus_shape_count_plus_text_count(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_mod_500_plus_shape_count_plus_text_count(EMPTY),
            fodg_file_size_mod_500_plus_shape_count_plus_text_count(MINIMAL),
            fodg_file_size_mod_500_plus_shape_count_plus_text_count(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_mod_500_plus_shape_count_plus_text_count(EMPTY) > 0


class TestFodgFileSizeDiv50TimesShapeCountPlus1:
    def test_empty_value(self):
        assert fodg_file_size_div_50_times_shape_count_plus_1(EMPTY) == 21

    def test_minimal_value(self):
        assert fodg_file_size_div_50_times_shape_count_plus_1(MINIMAL) == 58

    def test_shapes_value(self):
        assert fodg_file_size_div_50_times_shape_count_plus_1(SHAPES) == 128

    def test_returns_int(self):
        assert isinstance(fodg_file_size_div_50_times_shape_count_plus_1(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_div_50_times_shape_count_plus_1(EMPTY),
            fodg_file_size_div_50_times_shape_count_plus_1(MINIMAL),
            fodg_file_size_div_50_times_shape_count_plus_1(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_div_50_times_shape_count_plus_1(EMPTY) > 0
