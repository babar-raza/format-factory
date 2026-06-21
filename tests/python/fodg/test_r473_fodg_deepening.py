"""Sprint 244 FODG deepening — 2 new analytics functions, 12 tests.

Functions:
  fodg_file_size_mod_19_times_4_plus_shape_count_times_1000_plus_text_count_times_600
  fodg_file_size_mod_23_times_3_plus_shape_count_times_700_plus_text_count_times_300

Samples (samples/by-format/fodg/):
  empty-page.fodg       sz=1053, sc=0, tc=0
  minimal-drawing.fodg  sz=1473, sc=1, tc=1
  shapes-basic.fodg     sz=1628, sc=3, tc=2

Expected:
  fodg_file_size_mod_19_times_4_plus_shape_count_times_1000_plus_text_count_times_600:
    empty   = 1053%19*4 + 0*1000 + 0*600 = 8*4+0+0 = 32
    minimal = 1473%19*4 + 1*1000 + 1*600 = 10*4+1000+600 = 1640
    shapes  = 1628%19*4 + 3*1000 + 2*600 = 13*4+3000+1200 = 4252

  fodg_file_size_mod_23_times_3_plus_shape_count_times_700_plus_text_count_times_300:
    empty   = 1053%23*3 + 0*700 + 0*300 = 18*3+0+0 = 54
    minimal = 1473%23*3 + 1*700 + 1*300 = 1*3+700+300 = 1003
    shapes  = 1628%23*3 + 3*700 + 2*300 = 18*3+2100+600 = 2754
"""
from pathlib import Path

import pytest

from src.python.fodg import (
    fodg_file_size_mod_19_times_4_plus_shape_count_times_1000_plus_text_count_times_600,
    fodg_file_size_mod_23_times_3_plus_shape_count_times_700_plus_text_count_times_300,
)

_BASE = Path("samples/by-format/fodg")
EMPTY = _BASE / "empty-page.fodg"
MINIMAL = _BASE / "minimal-drawing.fodg"
SHAPES = _BASE / "shapes-basic.fodg"


class TestFodgFileSizeMod19Times4PlusShapeCountTimes1000PlusTextCountTimes600:
    def test_empty_value(self):
        assert fodg_file_size_mod_19_times_4_plus_shape_count_times_1000_plus_text_count_times_600(EMPTY) == 32

    def test_minimal_value(self):
        assert fodg_file_size_mod_19_times_4_plus_shape_count_times_1000_plus_text_count_times_600(MINIMAL) == 1640

    def test_shapes_value(self):
        assert fodg_file_size_mod_19_times_4_plus_shape_count_times_1000_plus_text_count_times_600(SHAPES) == 4252

    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_19_times_4_plus_shape_count_times_1000_plus_text_count_times_600(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_mod_19_times_4_plus_shape_count_times_1000_plus_text_count_times_600(EMPTY),
            fodg_file_size_mod_19_times_4_plus_shape_count_times_1000_plus_text_count_times_600(MINIMAL),
            fodg_file_size_mod_19_times_4_plus_shape_count_times_1000_plus_text_count_times_600(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_mod_19_times_4_plus_shape_count_times_1000_plus_text_count_times_600(EMPTY) > 0


class TestFodgFileSizeMod23Times3PlusShapeCountTimes700PlusTextCountTimes300:
    def test_empty_value(self):
        assert fodg_file_size_mod_23_times_3_plus_shape_count_times_700_plus_text_count_times_300(EMPTY) == 54

    def test_minimal_value(self):
        assert fodg_file_size_mod_23_times_3_plus_shape_count_times_700_plus_text_count_times_300(MINIMAL) == 1003

    def test_shapes_value(self):
        assert fodg_file_size_mod_23_times_3_plus_shape_count_times_700_plus_text_count_times_300(SHAPES) == 2754

    def test_returns_int(self):
        assert isinstance(fodg_file_size_mod_23_times_3_plus_shape_count_times_700_plus_text_count_times_300(EMPTY), int)

    def test_all_distinct(self):
        vals = [
            fodg_file_size_mod_23_times_3_plus_shape_count_times_700_plus_text_count_times_300(EMPTY),
            fodg_file_size_mod_23_times_3_plus_shape_count_times_700_plus_text_count_times_300(MINIMAL),
            fodg_file_size_mod_23_times_3_plus_shape_count_times_700_plus_text_count_times_300(SHAPES),
        ]
        assert len(set(vals)) == 3

    def test_positive(self):
        assert fodg_file_size_mod_23_times_3_plus_shape_count_times_700_plus_text_count_times_300(EMPTY) > 0
