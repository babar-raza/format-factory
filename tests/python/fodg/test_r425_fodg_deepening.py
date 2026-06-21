"""Tests for FODG product deepening sprint 196.

New functions:
  fodg_file_size_plus_shape_count_plus_text_count_times_2  — (sz+sc+tc)*2
  fodg_file_size_div_5_plus_shape_count_times_text_count  — sz//5 + sc*tc
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_plus_shape_count_plus_text_count_times_2,
    fodg_file_size_div_5_plus_shape_count_times_text_count,
)

_EMPTY = str(_REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg")
_MINIMAL = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
_SHAPES = str(_REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg")


class TestFodgFileSizePlusShapeCountPlusTextCountTimes2:
    def test_return_type(self):
        assert isinstance(fodg_file_size_plus_shape_count_plus_text_count_times_2(_EMPTY), int)

    def test_exact_2106_for_empty(self):
        # empty-page: sz=1053, sc=0, tc=0 → (1053+0+0)*2 = 2106
        assert fodg_file_size_plus_shape_count_plus_text_count_times_2(_EMPTY) == 2106

    def test_exact_2950_for_minimal(self):
        # minimal-drawing: sz=1473, sc=1, tc=1 → (1473+1+1)*2 = 2950
        assert fodg_file_size_plus_shape_count_plus_text_count_times_2(_MINIMAL) == 2950

    def test_exact_3266_for_shapes(self):
        # shapes-basic: sz=1628, sc=3, tc=2 → (1628+3+2)*2 = 3266
        assert fodg_file_size_plus_shape_count_plus_text_count_times_2(_SHAPES) == 3266

    def test_nonnegative(self):
        assert fodg_file_size_plus_shape_count_plus_text_count_times_2(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_file_size_plus_shape_count_plus_text_count_times_2(_SHAPES) == fodg_file_size_plus_shape_count_plus_text_count_times_2(_SHAPES)


class TestFodgFileSizeDiv5PlusShapeCountTimesTextCount:
    def test_return_type(self):
        assert isinstance(fodg_file_size_div_5_plus_shape_count_times_text_count(_EMPTY), int)

    def test_exact_210_for_empty(self):
        # empty-page: sz=1053, sc=0, tc=0 → 1053//5 + 0*0 = 210
        assert fodg_file_size_div_5_plus_shape_count_times_text_count(_EMPTY) == 210

    def test_exact_295_for_minimal(self):
        # minimal-drawing: sz=1473, sc=1, tc=1 → 1473//5 + 1*1 = 295
        assert fodg_file_size_div_5_plus_shape_count_times_text_count(_MINIMAL) == 295

    def test_exact_331_for_shapes(self):
        # shapes-basic: sz=1628, sc=3, tc=2 → 1628//5 + 3*2 = 331
        assert fodg_file_size_div_5_plus_shape_count_times_text_count(_SHAPES) == 331

    def test_nonnegative(self):
        assert fodg_file_size_div_5_plus_shape_count_times_text_count(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_file_size_div_5_plus_shape_count_times_text_count(_SHAPES) == fodg_file_size_div_5_plus_shape_count_times_text_count(_SHAPES)
