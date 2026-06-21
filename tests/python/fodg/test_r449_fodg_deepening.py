"""Sprint 220 FODG deepening — 2 new analytics functions, 12 tests.

Functions:
  fodg_file_size_mod_300_plus_shape_count_times_text_count_times_200
  fodg_file_size_plus_shape_count_times_100_div_text_count_plus_1

Samples (samples/by-format/fodg/):
  empty-page.fodg      sz=1053, sc=0, tc=0
  minimal-drawing.fodg sz=1473, sc=1, tc=1
  shapes-basic.fodg    sz=1628, sc=3, tc=2

Expected:
  fodg_file_size_mod_300_plus_shape_count_times_text_count_times_200:
    empty   = 1053%300 + 0*0*200   = 153
    minimal = 1473%300 + 1*1*200   = 473
    shapes  = 1628%300 + 3*2*200   = 1328

  fodg_file_size_plus_shape_count_times_100_div_text_count_plus_1:
    empty   = (1053 + 0*100) // (0+1)  = 1053
    minimal = (1473 + 1*100) // (1+1)  = 786
    shapes  = (1628 + 3*100) // (2+1)  = 642
"""
from pathlib import Path

import pytest

from src.python.fodg import (
    fodg_file_size_mod_300_plus_shape_count_times_text_count_times_200,
    fodg_file_size_plus_shape_count_times_100_div_text_count_plus_1,
)

_FODG = Path("samples/by-format/fodg")
EMPTY = _FODG / "empty-page.fodg"
MINIMAL = _FODG / "minimal-drawing.fodg"
SHAPES = _FODG / "shapes-basic.fodg"


class TestFodgFileSizeMod300PlusShapeCountTimesTextCountTimes200:
    def test_empty_value(self):
        assert fodg_file_size_mod_300_plus_shape_count_times_text_count_times_200(EMPTY) == 153

    def test_minimal_value(self):
        assert fodg_file_size_mod_300_plus_shape_count_times_text_count_times_200(MINIMAL) == 473

    def test_shapes_value(self):
        assert fodg_file_size_mod_300_plus_shape_count_times_text_count_times_200(SHAPES) == 1328

    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_300_plus_shape_count_times_text_count_times_200(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_mod_300_plus_shape_count_times_text_count_times_200(EMPTY),
            fodg_file_size_mod_300_plus_shape_count_times_text_count_times_200(MINIMAL),
            fodg_file_size_mod_300_plus_shape_count_times_text_count_times_200(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_mod_300_plus_shape_count_times_text_count_times_200(EMPTY) > 0


class TestFodgFileSizePlusShapeCountTimes100DivTextCountPlus1:
    def test_empty_value(self):
        assert fodg_file_size_plus_shape_count_times_100_div_text_count_plus_1(EMPTY) == 1053

    def test_minimal_value(self):
        assert fodg_file_size_plus_shape_count_times_100_div_text_count_plus_1(MINIMAL) == 786

    def test_shapes_value(self):
        assert fodg_file_size_plus_shape_count_times_100_div_text_count_plus_1(SHAPES) == 642

    def test_returns_int(self):
        assert isinstance(fodg_file_size_plus_shape_count_times_100_div_text_count_plus_1(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_plus_shape_count_times_100_div_text_count_plus_1(EMPTY),
            fodg_file_size_plus_shape_count_times_100_div_text_count_plus_1(MINIMAL),
            fodg_file_size_plus_shape_count_times_100_div_text_count_plus_1(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_plus_shape_count_times_100_div_text_count_plus_1(EMPTY) > 0
