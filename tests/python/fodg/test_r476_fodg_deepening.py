"""Sprint 247 FODG deepening — 2 new analytics functions, 12 tests.

Functions:
  fodg_file_size_mod_29_times_2_plus_shape_count_times_1100_plus_text_count_times_800
  fodg_file_size_mod_17_times_5_plus_shape_count_times_850_plus_text_count_times_450

Samples (samples/by-format/fodg/):
  empty-page.fodg       sz=1053, sc=0, tc=0
  minimal-drawing.fodg  sz=1473, sc=1, tc=1
  shapes-basic.fodg     sz=1628, sc=3, tc=2

Expected:
  fodg_file_size_mod_29_times_2_plus_shape_count_times_1100_plus_text_count_times_800:
    empty   = 1053%29*2 + 0*1100 + 0*800 = 9*2+0+0 = 18
    minimal = 1473%29*2 + 1*1100 + 1*800 = 23*2+1100+800 = 1946
    shapes  = 1628%29*2 + 3*1100 + 2*800 = 4*2+3300+1600 = 4908

  fodg_file_size_mod_17_times_5_plus_shape_count_times_850_plus_text_count_times_450:
    empty   = 1053%17*5 + 0*850 + 0*450 = 16*5+0+0 = 80
    minimal = 1473%17*5 + 1*850 + 1*450 = 11*5+850+450 = 1355
    shapes  = 1628%17*5 + 3*850 + 2*450 = 13*5+2550+900 = 3515
"""
from pathlib import Path

import pytest

from src.python.fodg import (
    fodg_file_size_mod_29_times_2_plus_shape_count_times_1100_plus_text_count_times_800,
    fodg_file_size_mod_17_times_5_plus_shape_count_times_850_plus_text_count_times_450,
)

_BASE = Path("samples/by-format/fodg")
EMPTY = _BASE / "empty-page.fodg"
MINIMAL = _BASE / "minimal-drawing.fodg"
SHAPES = _BASE / "shapes-basic.fodg"


class TestFodgFileSizeMod29Times2PlusShapeCountTimes1100PlusTextCountTimes800:
    def test_empty_value(self):
        assert fodg_file_size_mod_29_times_2_plus_shape_count_times_1100_plus_text_count_times_800(EMPTY) == 18

    def test_minimal_value(self):
        assert fodg_file_size_mod_29_times_2_plus_shape_count_times_1100_plus_text_count_times_800(MINIMAL) == 1946

    def test_shapes_value(self):
        assert fodg_file_size_mod_29_times_2_plus_shape_count_times_1100_plus_text_count_times_800(SHAPES) == 4908

    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_29_times_2_plus_shape_count_times_1100_plus_text_count_times_800(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_mod_29_times_2_plus_shape_count_times_1100_plus_text_count_times_800(EMPTY),
            fodg_file_size_mod_29_times_2_plus_shape_count_times_1100_plus_text_count_times_800(MINIMAL),
            fodg_file_size_mod_29_times_2_plus_shape_count_times_1100_plus_text_count_times_800(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_mod_29_times_2_plus_shape_count_times_1100_plus_text_count_times_800(EMPTY) > 0


class TestFodgFileSizeMod17Times5PlusShapeCountTimes850PlusTextCountTimes450:
    def test_empty_value(self):
        assert fodg_file_size_mod_17_times_5_plus_shape_count_times_850_plus_text_count_times_450(EMPTY) == 80

    def test_minimal_value(self):
        assert fodg_file_size_mod_17_times_5_plus_shape_count_times_850_plus_text_count_times_450(MINIMAL) == 1355

    def test_shapes_value(self):
        assert fodg_file_size_mod_17_times_5_plus_shape_count_times_850_plus_text_count_times_450(SHAPES) == 3515

    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_17_times_5_plus_shape_count_times_850_plus_text_count_times_450(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_mod_17_times_5_plus_shape_count_times_850_plus_text_count_times_450(EMPTY),
            fodg_file_size_mod_17_times_5_plus_shape_count_times_850_plus_text_count_times_450(MINIMAL),
            fodg_file_size_mod_17_times_5_plus_shape_count_times_850_plus_text_count_times_450(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_mod_17_times_5_plus_shape_count_times_850_plus_text_count_times_450(EMPTY) > 0
