"""Sprint 202 FODG deepening — 2 new analytics functions, 12 tests.

Functions:
  fodg_file_size_div_10_times_shape_count_plus_text_count_times_50
  fodg_shape_count_times_text_count_times_100_plus_file_size_div_10

Samples (samples/by-format/fodg/):
  empty-page.fodg      sz=1053, sc=0, tc=0
  minimal-drawing.fodg sz=1473, sc=1, tc=1
  shapes-basic.fodg    sz=1628, sc=3, tc=2

Expected:
  fodg_file_size_div_10_times_shape_count_plus_text_count_times_50:
    empty   = 1053//10 * 0 + 0*50    = 0
    minimal = 1473//10 * 1 + 1*50    = 197
    shapes  = 1628//10 * 3 + 2*50    = 586

  fodg_shape_count_times_text_count_times_100_plus_file_size_div_10:
    empty   = 0*0*100 + 1053//10     = 105
    minimal = 1*1*100 + 1473//10     = 247
    shapes  = 3*2*100 + 1628//10     = 762
"""
from pathlib import Path

import pytest

from src.python.fodg import (
    fodg_file_size_div_10_times_shape_count_plus_text_count_times_50,
    fodg_shape_count_times_text_count_times_100_plus_file_size_div_10,
)

_FODG = Path("samples/by-format/fodg")
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"


class TestFodgFileSizeDiv10TimesShapeCountPlusTextCountTimes50:
    def test_empty_value(self):
        assert fodg_file_size_div_10_times_shape_count_plus_text_count_times_50(EMPTY) == 0

    def test_minimal_value(self):
        assert fodg_file_size_div_10_times_shape_count_plus_text_count_times_50(MINIMAL) == 197

    def test_shapes_value(self):
        assert fodg_file_size_div_10_times_shape_count_plus_text_count_times_50(SHAPES) == 586

    def test_returns_int(self):
        assert isinstance(fodg_file_size_div_10_times_shape_count_plus_text_count_times_50(EMPTY), int)

    def test_shapes_largest(self):
        assert fodg_file_size_div_10_times_shape_count_plus_text_count_times_50(SHAPES) > fodg_file_size_div_10_times_shape_count_plus_text_count_times_50(MINIMAL)

    def test_non_negative(self):
        assert fodg_file_size_div_10_times_shape_count_plus_text_count_times_50(EMPTY) >= 0


class TestFodgShapeCountTimesTextCountTimes100PlusFileSizeDiv10:
    def test_empty_value(self):
        assert fodg_shape_count_times_text_count_times_100_plus_file_size_div_10(EMPTY) == 105

    def test_minimal_value(self):
        assert fodg_shape_count_times_text_count_times_100_plus_file_size_div_10(MINIMAL) == 247

    def test_shapes_value(self):
        assert fodg_shape_count_times_text_count_times_100_plus_file_size_div_10(SHAPES) == 762

    def test_returns_int(self):
        assert isinstance(fodg_shape_count_times_text_count_times_100_plus_file_size_div_10(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_shape_count_times_text_count_times_100_plus_file_size_div_10(EMPTY),
            fodg_shape_count_times_text_count_times_100_plus_file_size_div_10(MINIMAL),
            fodg_shape_count_times_text_count_times_100_plus_file_size_div_10(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_shape_count_times_text_count_times_100_plus_file_size_div_10(EMPTY) > 0
