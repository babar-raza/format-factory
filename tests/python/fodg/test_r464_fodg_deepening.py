"""Sprint 235 FODG deepening — 2 new analytics functions, 12 tests.

Functions:
  fodg_file_size_plus_shape_count_times_600_plus_text_count_times_400_div_10
  fodg_file_size_mod_17_plus_shape_count_times_700_plus_text_count_times_500

Samples (samples/by-format/fodg/):
  empty-page.fodg      sz=1053, sc=0, tc=0
  minimal-drawing.fodg sz=1473, sc=1, tc=1
  shapes-basic.fodg    sz=1628, sc=3, tc=2

Expected:
  fodg_file_size_plus_shape_count_times_600_plus_text_count_times_400_div_10:
    empty   = (1053+0+0)//10 = 105
    minimal = (1473+1*600+1*400)//10 = 2473//10 = 247
    shapes  = (1628+3*600+2*400)//10 = (1628+1800+800)//10 = 4228//10 = 422

  fodg_file_size_mod_17_plus_shape_count_times_700_plus_text_count_times_500:
    empty   = 1053%17 + 0*700 + 0*500 = 16
    minimal = 1473%17 + 1*700 + 1*500 = 11+1200 = 1211
    shapes  = 1628%17 + 3*700 + 2*500 = 13+2100+1000 = 3113
"""
from pathlib import Path

import pytest

from src.python.fodg import (
    fodg_file_size_plus_shape_count_times_600_plus_text_count_times_400_div_10,
    fodg_file_size_mod_17_plus_shape_count_times_700_plus_text_count_times_500,
)

_SAMPLES = Path("samples/by-format/fodg")
EMPTY = _SAMPLES / "empty-page.fodg"
MINIMAL = _SAMPLES / "minimal-drawing.fodg"
SHAPES = _SAMPLES / "shapes-basic.fodg"


class TestFodgFileSizePlusShapeCountTimes600PlusTextCountTimes400Div10:
    def test_empty_value(self):
        assert fodg_file_size_plus_shape_count_times_600_plus_text_count_times_400_div_10(EMPTY) == 105

    def test_minimal_value(self):
        assert fodg_file_size_plus_shape_count_times_600_plus_text_count_times_400_div_10(MINIMAL) == 247

    def test_shapes_value(self):
        assert fodg_file_size_plus_shape_count_times_600_plus_text_count_times_400_div_10(SHAPES) == 422

    def test_returns_int(self):
        assert isinstance(fodg_file_size_plus_shape_count_times_600_plus_text_count_times_400_div_10(MINIMAL), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_plus_shape_count_times_600_plus_text_count_times_400_div_10(EMPTY),
            fodg_file_size_plus_shape_count_times_600_plus_text_count_times_400_div_10(MINIMAL),
            fodg_file_size_plus_shape_count_times_600_plus_text_count_times_400_div_10(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_plus_shape_count_times_600_plus_text_count_times_400_div_10(EMPTY) > 0


class TestFodgFileSizeMod17PlusShapeCountTimes700PlusTextCountTimes500:
    def test_empty_value(self):
        assert fodg_file_size_mod_17_plus_shape_count_times_700_plus_text_count_times_500(EMPTY) == 16

    def test_minimal_value(self):
        assert fodg_file_size_mod_17_plus_shape_count_times_700_plus_text_count_times_500(MINIMAL) == 1211

    def test_shapes_value(self):
        assert fodg_file_size_mod_17_plus_shape_count_times_700_plus_text_count_times_500(SHAPES) == 3113

    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_17_plus_shape_count_times_700_plus_text_count_times_500(MINIMAL), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_mod_17_plus_shape_count_times_700_plus_text_count_times_500(EMPTY),
            fodg_file_size_mod_17_plus_shape_count_times_700_plus_text_count_times_500(MINIMAL),
            fodg_file_size_mod_17_plus_shape_count_times_700_plus_text_count_times_500(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_mod_17_plus_shape_count_times_700_plus_text_count_times_500(EMPTY) > 0
