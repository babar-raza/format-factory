"""Tests for FODG product deepening sprint 184.

New functions:
  fodg_file_size_minus_shape_count_times_50  — sz - sc*50, min 0
  fodg_shape_count_times_text_count_plus_file_size_div_100  — sc*tc + sz//100
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_minus_shape_count_times_50,
    fodg_shape_count_times_text_count_plus_file_size_div_100,
)

_EMPTY = str(_REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg")
_MINIMAL = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
_SHAPES = str(_REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg")


class TestFodgFileSizeMinusShapeCountTimes50:
    def test_return_type(self):
        assert isinstance(fodg_file_size_minus_shape_count_times_50(_EMPTY), int)

    def test_exact_1053_for_empty(self):
        # empty-page: sz=1053, sc=0 → 1053 - 0 = 1053
        assert fodg_file_size_minus_shape_count_times_50(_EMPTY) == 1053

    def test_exact_1423_for_minimal(self):
        # minimal-drawing: sz=1473, sc=1 → 1473 - 50 = 1423
        assert fodg_file_size_minus_shape_count_times_50(_MINIMAL) == 1423

    def test_exact_1478_for_shapes(self):
        # shapes-basic: sz=1628, sc=3 → 1628 - 150 = 1478
        assert fodg_file_size_minus_shape_count_times_50(_SHAPES) == 1478

    def test_nonnegative(self):
        assert fodg_file_size_minus_shape_count_times_50(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_file_size_minus_shape_count_times_50(_SHAPES) == fodg_file_size_minus_shape_count_times_50(_SHAPES)


class TestFodgShapeCountTimesTextCountPlusFileSizeDiv100:
    def test_return_type(self):
        assert isinstance(fodg_shape_count_times_text_count_plus_file_size_div_100(_EMPTY), int)

    def test_exact_10_for_empty(self):
        # empty-page: sc=0, tc=0, sz=1053 → 0*0 + 1053//100 = 10
        assert fodg_shape_count_times_text_count_plus_file_size_div_100(_EMPTY) == 10

    def test_exact_15_for_minimal(self):
        # minimal-drawing: sc=1, tc=1, sz=1473 → 1*1 + 1473//100 = 1 + 14 = 15
        assert fodg_shape_count_times_text_count_plus_file_size_div_100(_MINIMAL) == 15

    def test_exact_22_for_shapes(self):
        # shapes-basic: sc=3, tc=2, sz=1628 → 3*2 + 1628//100 = 6 + 16 = 22
        assert fodg_shape_count_times_text_count_plus_file_size_div_100(_SHAPES) == 22

    def test_nonnegative(self):
        assert fodg_shape_count_times_text_count_plus_file_size_div_100(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_shape_count_times_text_count_plus_file_size_div_100(_SHAPES) == fodg_shape_count_times_text_count_plus_file_size_div_100(_SHAPES)
