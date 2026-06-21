"""Tests for FODG product deepening sprint 190.

New functions:
  fodg_file_size_div_shape_count_plus_1  — sz // (sc+1)
  fodg_file_size_plus_shape_count_times_text_count_times_10  — sz + sc*tc*10
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_div_shape_count_plus_1,
    fodg_file_size_plus_shape_count_times_text_count_times_10,
)

_EMPTY = str(_REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg")
_MINIMAL = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
_SHAPES = str(_REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg")


class TestFodgFileSizeDivShapeCountPlus1:
    def test_return_type(self):
        assert isinstance(fodg_file_size_div_shape_count_plus_1(_EMPTY), int)

    def test_exact_1053_for_empty(self):
        # empty-page: sz=1053, sc=0 → 1053//(0+1) = 1053
        assert fodg_file_size_div_shape_count_plus_1(_EMPTY) == 1053

    def test_exact_736_for_minimal(self):
        # minimal-drawing: sz=1473, sc=1 → 1473//(1+1) = 736
        assert fodg_file_size_div_shape_count_plus_1(_MINIMAL) == 736

    def test_exact_407_for_shapes(self):
        # shapes-basic: sz=1628, sc=3 → 1628//(3+1) = 407
        assert fodg_file_size_div_shape_count_plus_1(_SHAPES) == 407

    def test_nonnegative(self):
        assert fodg_file_size_div_shape_count_plus_1(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_file_size_div_shape_count_plus_1(_SHAPES) == fodg_file_size_div_shape_count_plus_1(_SHAPES)


class TestFodgFileSizePlusShapeCountTimesTextCountTimes10:
    def test_return_type(self):
        assert isinstance(fodg_file_size_plus_shape_count_times_text_count_times_10(_EMPTY), int)

    def test_exact_1053_for_empty(self):
        # empty-page: sz=1053, sc=0, tc=0 → 1053 + 0*0*10 = 1053
        assert fodg_file_size_plus_shape_count_times_text_count_times_10(_EMPTY) == 1053

    def test_exact_1483_for_minimal(self):
        # minimal-drawing: sz=1473, sc=1, tc=1 → 1473 + 1*1*10 = 1483
        assert fodg_file_size_plus_shape_count_times_text_count_times_10(_MINIMAL) == 1483

    def test_exact_1688_for_shapes(self):
        # shapes-basic: sz=1628, sc=3, tc=2 → 1628 + 3*2*10 = 1688
        assert fodg_file_size_plus_shape_count_times_text_count_times_10(_SHAPES) == 1688

    def test_nonnegative(self):
        assert fodg_file_size_plus_shape_count_times_text_count_times_10(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_file_size_plus_shape_count_times_text_count_times_10(_SHAPES) == fodg_file_size_plus_shape_count_times_text_count_times_10(_SHAPES)
