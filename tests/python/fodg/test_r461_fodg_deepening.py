"""Sprint 232 FODG deepening — 2 new analytics functions, 12 tests.

Functions:
  fodg_file_size_mod_11_plus_shape_count_times_500_plus_text_count_times_350
  fodg_file_size_times_2_mod_500_plus_shape_count_times_200_plus_text_count_times_150

Samples (samples/by-format/fodg/):
  empty-page.fodg      sz=1053, sc=0, tc=0
  minimal-drawing.fodg sz=1473, sc=1, tc=1
  shapes-basic.fodg    sz=1628, sc=3, tc=2

Expected:
  fodg_file_size_mod_11_plus_shape_count_times_500_plus_text_count_times_350:
    empty   = 1053%11 + 0*500 + 0*350 = 8
    minimal = 1473%11 + 1*500 + 1*350 = 10+850 = 860
    shapes  = 1628%11 + 3*500 + 2*350 = 0+1500+700 = 2200

  fodg_file_size_times_2_mod_500_plus_shape_count_times_200_plus_text_count_times_150:
    empty   = 1053*2%500 + 0*200 + 0*150 = 2106%500 = 106
    minimal = 1473*2%500 + 1*200 + 1*150 = 2946%500+350 = 446+350 = 796
    shapes  = 1628*2%500 + 3*200 + 2*150 = 3256%500+900 = 256+900 = 1156
"""
from pathlib import Path

import pytest

from src.python.fodg import (
    fodg_file_size_mod_11_plus_shape_count_times_500_plus_text_count_times_350,
    fodg_file_size_times_2_mod_500_plus_shape_count_times_200_plus_text_count_times_150,
)

_SAMPLES = Path("samples/by-format/fodg")
EMPTY = _SAMPLES / "empty-page.fodg"
MINIMAL = _SAMPLES / "minimal-drawing.fodg"
SHAPES = _SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizeMod11PlusShapeCountTimes500PlusTextCountTimes350:
    def test_empty_value(self):
        assert fodg_file_size_mod_11_plus_shape_count_times_500_plus_text_count_times_350(EMPTY) == 8

    def test_minimal_value(self):
        assert fodg_file_size_mod_11_plus_shape_count_times_500_plus_text_count_times_350(MINIMAL) == 860

    def test_shapes_value(self):
        assert fodg_file_size_mod_11_plus_shape_count_times_500_plus_text_count_times_350(SHAPES) == 2200

    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_11_plus_shape_count_times_500_plus_text_count_times_350(MINIMAL), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_mod_11_plus_shape_count_times_500_plus_text_count_times_350(EMPTY),
            fodg_file_size_mod_11_plus_shape_count_times_500_plus_text_count_times_350(MINIMAL),
            fodg_file_size_mod_11_plus_shape_count_times_500_plus_text_count_times_350(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_mod_11_plus_shape_count_times_500_plus_text_count_times_350(EMPTY) > 0


class TestFodgFileSizeTimes2Mod500PlusShapeCountTimes200PlusTextCountTimes150:
    def test_empty_value(self):
        assert fodg_file_size_times_2_mod_500_plus_shape_count_times_200_plus_text_count_times_150(EMPTY) == 106

    def test_minimal_value(self):
        assert fodg_file_size_times_2_mod_500_plus_shape_count_times_200_plus_text_count_times_150(MINIMAL) == 796

    def test_shapes_value(self):
        assert fodg_file_size_times_2_mod_500_plus_shape_count_times_200_plus_text_count_times_150(SHAPES) == 1156

    def test_returns_int(self):
        assert isinstance(fodg_file_size_times_2_mod_500_plus_shape_count_times_200_plus_text_count_times_150(MINIMAL), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_times_2_mod_500_plus_shape_count_times_200_plus_text_count_times_150(EMPTY),
            fodg_file_size_times_2_mod_500_plus_shape_count_times_200_plus_text_count_times_150(MINIMAL),
            fodg_file_size_times_2_mod_500_plus_shape_count_times_200_plus_text_count_times_150(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_times_2_mod_500_plus_shape_count_times_200_plus_text_count_times_150(EMPTY) > 0
