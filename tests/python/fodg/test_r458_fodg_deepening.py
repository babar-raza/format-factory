"""Sprint 229 FODG deepening — 2 new analytics functions, 12 tests.

Functions:
  fodg_file_size_mod_7_plus_shape_count_times_400_plus_text_count_times_250
  fodg_file_size_div_100_times_shape_count_plus_1_plus_text_count_times_50

Samples (samples/by-format/fodg/):
  empty-page.fodg      sz=1053, sc=0, tc=0
  minimal-drawing.fodg sz=1473, sc=1, tc=1
  shapes-basic.fodg    sz=1628, sc=3, tc=2

Expected:
  fodg_file_size_mod_7_plus_shape_count_times_400_plus_text_count_times_250:
    empty   = 1053%7 + 0*400 + 0*250 = 3
    minimal = 1473%7 + 1*400 + 1*250 = 3+650 = 653
    shapes  = 1628%7 + 3*400 + 2*250 = 4+1200+500 = 1704

  fodg_file_size_div_100_times_shape_count_plus_1_plus_text_count_times_50:
    empty   = 1053//100 * (0+1) + 0*50 = 10
    minimal = 1473//100 * (1+1) + 1*50 = 14*2+50 = 78
    shapes  = 1628//100 * (3+1) + 2*50 = 16*4+100 = 164
"""
from pathlib import Path

import pytest

from src.python.fodg import (
    fodg_file_size_mod_7_plus_shape_count_times_400_plus_text_count_times_250,
    fodg_file_size_div_100_times_shape_count_plus_1_plus_text_count_times_50,
)

_SAMPLES = Path("samples/by-format/fodg")
EMPTY = _SAMPLES / "empty-page.fodg"
MINIMAL = _SAMPLES / "minimal-drawing.fodg"
SHAPES = _SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod7PlusShapeCountTimes400PlusTextCountTimes250:
    def test_empty_value(self):
        assert fodg_file_size_mod_7_plus_shape_count_times_400_plus_text_count_times_250(EMPTY) == 3

    def test_minimal_value(self):
        assert fodg_file_size_mod_7_plus_shape_count_times_400_plus_text_count_times_250(MINIMAL) == 653

    def test_shapes_value(self):
        assert fodg_file_size_mod_7_plus_shape_count_times_400_plus_text_count_times_250(SHAPES) == 1704

    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_7_plus_shape_count_times_400_plus_text_count_times_250(MINIMAL), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_mod_7_plus_shape_count_times_400_plus_text_count_times_250(EMPTY),
            fodg_file_size_mod_7_plus_shape_count_times_400_plus_text_count_times_250(MINIMAL),
            fodg_file_size_mod_7_plus_shape_count_times_400_plus_text_count_times_250(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_mod_7_plus_shape_count_times_400_plus_text_count_times_250(MINIMAL) > 0


class TestFodgFileSizeDiv100TimesShapeCountPlus1PlusTextCountTimes50:
    def test_empty_value(self):
        assert fodg_file_size_div_100_times_shape_count_plus_1_plus_text_count_times_50(EMPTY) == 10

    def test_minimal_value(self):
        assert fodg_file_size_div_100_times_shape_count_plus_1_plus_text_count_times_50(MINIMAL) == 78

    def test_shapes_value(self):
        assert fodg_file_size_div_100_times_shape_count_plus_1_plus_text_count_times_50(SHAPES) == 164

    def test_returns_int(self):
        assert isinstance(fodg_file_size_div_100_times_shape_count_plus_1_plus_text_count_times_50(MINIMAL), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_div_100_times_shape_count_plus_1_plus_text_count_times_50(EMPTY),
            fodg_file_size_div_100_times_shape_count_plus_1_plus_text_count_times_50(MINIMAL),
            fodg_file_size_div_100_times_shape_count_plus_1_plus_text_count_times_50(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_div_100_times_shape_count_plus_1_plus_text_count_times_50(EMPTY) > 0
