"""Sprint 238 FODG deepening — 2 new analytics functions, 12 tests.

Functions:
  fodg_file_size_mod_23_plus_shape_count_times_800_plus_text_count_times_600
  fodg_file_size_times_3_mod_1000_plus_shape_count_times_100_plus_text_count_times_80

Samples (samples/by-format/fodg/):
  empty-page.fodg      sz=1053, sc=0, tc=0
  minimal-drawing.fodg sz=1473, sc=1, tc=1
  shapes-basic.fodg    sz=1628, sc=3, tc=2

Expected:
  fodg_file_size_mod_23_plus_shape_count_times_800_plus_text_count_times_600:
    empty   = 1053%23 + 0*800 + 0*600 = 18
    minimal = 1473%23 + 1*800 + 1*600 = 1+1400 = 1401
    shapes  = 1628%23 + 3*800 + 2*600 = 18+2400+1200 = 3618

  fodg_file_size_times_3_mod_1000_plus_shape_count_times_100_plus_text_count_times_80:
    empty   = 1053*3%1000 + 0*100 + 0*80 = 3159%1000 = 159
    minimal = 1473*3%1000 + 1*100 + 1*80 = 4419%1000+180 = 419+180 = 599
    shapes  = 1628*3%1000 + 3*100 + 2*80 = 4884%1000+460 = 884+460 = 1344
"""
from pathlib import Path

import pytest

from src.python.fodg import (
    fodg_file_size_mod_23_plus_shape_count_times_800_plus_text_count_times_600,
    fodg_file_size_times_3_mod_1000_plus_shape_count_times_100_plus_text_count_times_80,
)

_SAMPLES = Path("samples/by-format/fodg")
EMPTY = _SAMPLES / "empty-page.fodg"
MINIMAL = _SAMPLES / "minimal-drawing.fodg"
SHAPES = _SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod23PlusShapeCountTimes800PlusTextCountTimes600:
    def test_empty_value(self):
        assert fodg_file_size_mod_23_plus_shape_count_times_800_plus_text_count_times_600(EMPTY) == 18

    def test_minimal_value(self):
        assert fodg_file_size_mod_23_plus_shape_count_times_800_plus_text_count_times_600(MINIMAL) == 1401

    def test_shapes_value(self):
        assert fodg_file_size_mod_23_plus_shape_count_times_800_plus_text_count_times_600(SHAPES) == 3618

    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_23_plus_shape_count_times_800_plus_text_count_times_600(MINIMAL), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_mod_23_plus_shape_count_times_800_plus_text_count_times_600(EMPTY),
            fodg_file_size_mod_23_plus_shape_count_times_800_plus_text_count_times_600(MINIMAL),
            fodg_file_size_mod_23_plus_shape_count_times_800_plus_text_count_times_600(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_mod_23_plus_shape_count_times_800_plus_text_count_times_600(EMPTY) > 0


class TestFodgFileSizeTimes3Mod1000PlusShapeCountTimes100PlusTextCountTimes80:
    def test_empty_value(self):
        assert fodg_file_size_times_3_mod_1000_plus_shape_count_times_100_plus_text_count_times_80(EMPTY) == 159

    def test_minimal_value(self):
        assert fodg_file_size_times_3_mod_1000_plus_shape_count_times_100_plus_text_count_times_80(MINIMAL) == 599

    def test_shapes_value(self):
        assert fodg_file_size_times_3_mod_1000_plus_shape_count_times_100_plus_text_count_times_80(SHAPES) == 1344

    def test_returns_int(self):
        assert isinstance(fodg_file_size_times_3_mod_1000_plus_shape_count_times_100_plus_text_count_times_80(MINIMAL), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_times_3_mod_1000_plus_shape_count_times_100_plus_text_count_times_80(EMPTY),
            fodg_file_size_times_3_mod_1000_plus_shape_count_times_100_plus_text_count_times_80(MINIMAL),
            fodg_file_size_times_3_mod_1000_plus_shape_count_times_100_plus_text_count_times_80(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_times_3_mod_1000_plus_shape_count_times_100_plus_text_count_times_80(EMPTY) > 0
