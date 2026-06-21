"""Sprint 241 FODG deepening — 2 new analytics functions, 12 tests.

Functions:
  fodg_file_size_mod_11_times_3_plus_shape_count_times_900_plus_text_count_times_700
  fodg_file_size_mod_7_times_50_plus_shape_count_times_800_plus_text_count_times_500

Samples (samples/by-format/fodg/):
  empty-page.fodg       sz=1053, sc=0, tc=0
  minimal-drawing.fodg  sz=1473, sc=1, tc=1
  shapes-basic.fodg     sz=1628, sc=3, tc=2

Expected:
  fodg_file_size_mod_11_times_3_plus_shape_count_times_900_plus_text_count_times_700:
    empty   = 1053%11*3 + 0*900 + 0*700 = 8*3+0+0 = 24
    minimal = 1473%11*3 + 1*900 + 1*700 = 10*3+900+700 = 1630
    shapes  = 1628%11*3 + 3*900 + 2*700 = 0*3+2700+1400 = 4100

  fodg_file_size_mod_7_times_50_plus_shape_count_times_800_plus_text_count_times_500:
    empty   = 1053%7*50 + 0*800 + 0*500 = 3*50+0+0 = 150
    minimal = 1473%7*50 + 1*800 + 1*500 = 3*50+800+500 = 1450
    shapes  = 1628%7*50 + 3*800 + 2*500 = 4*50+2400+1000 = 3600
"""
from pathlib import Path

import pytest

from src.python.fodg import (
    fodg_file_size_mod_11_times_3_plus_shape_count_times_900_plus_text_count_times_700,
    fodg_file_size_mod_7_times_50_plus_shape_count_times_800_plus_text_count_times_500,
)

_BASE = Path("samples/by-format/fodg")
EMPTY = _BASE / "empty-page.fodg"
MINIMAL = _BASE / "minimal-drawing.fodg"
SHAPES = _BASE / "shapes-basic.fodg"


class TestFodgFileSizeMod11Times3PlusShapeCountTimes900PlusTextCountTimes700:
    def test_empty_value(self):
        assert fodg_file_size_mod_11_times_3_plus_shape_count_times_900_plus_text_count_times_700(EMPTY) == 24

    def test_minimal_value(self):
        assert fodg_file_size_mod_11_times_3_plus_shape_count_times_900_plus_text_count_times_700(MINIMAL) == 1630

    def test_shapes_value(self):
        assert fodg_file_size_mod_11_times_3_plus_shape_count_times_900_plus_text_count_times_700(SHAPES) == 4100

    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_11_times_3_plus_shape_count_times_900_plus_text_count_times_700(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_mod_11_times_3_plus_shape_count_times_900_plus_text_count_times_700(EMPTY),
            fodg_file_size_mod_11_times_3_plus_shape_count_times_900_plus_text_count_times_700(MINIMAL),
            fodg_file_size_mod_11_times_3_plus_shape_count_times_900_plus_text_count_times_700(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_mod_11_times_3_plus_shape_count_times_900_plus_text_count_times_700(EMPTY) > 0


class TestFodgFileSizeMod7Times50PlusShapeCountTimes800PlusTextCountTimes500:
    def test_empty_value(self):
        assert fodg_file_size_mod_7_times_50_plus_shape_count_times_800_plus_text_count_times_500(EMPTY) == 150

    def test_minimal_value(self):
        assert fodg_file_size_mod_7_times_50_plus_shape_count_times_800_plus_text_count_times_500(MINIMAL) == 1450

    def test_shapes_value(self):
        assert fodg_file_size_mod_7_times_50_plus_shape_count_times_800_plus_text_count_times_500(SHAPES) == 3600

    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_7_times_50_plus_shape_count_times_800_plus_text_count_times_500(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_mod_7_times_50_plus_shape_count_times_800_plus_text_count_times_500(EMPTY),
            fodg_file_size_mod_7_times_50_plus_shape_count_times_800_plus_text_count_times_500(MINIMAL),
            fodg_file_size_mod_7_times_50_plus_shape_count_times_800_plus_text_count_times_500(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_mod_7_times_50_plus_shape_count_times_800_plus_text_count_times_500(EMPTY) > 0
