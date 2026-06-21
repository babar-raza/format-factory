"""Tests for FODG product deepening sprint 178.

New functions:
  fodg_file_size_div_20  — file_size // 20
  fodg_shape_count_squared_plus_page_count_times_10  — sc*sc + pg*10
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_file_size_div_20,
    fodg_shape_count_squared_plus_page_count_times_10,
)

_EMPTY = str(_REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg")
_MINIMAL = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
_SHAPES = str(_REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg")


class TestFodgFileSizeDiv20:
    def test_return_type(self):
        assert isinstance(fodg_file_size_div_20(_EMPTY), int)

    def test_exact_52_for_empty(self):
        # empty-page: sz=1053 → 1053//20 = 52
        assert fodg_file_size_div_20(_EMPTY) == 52

    def test_exact_73_for_minimal(self):
        # minimal-drawing: sz=1473 → 1473//20 = 73
        assert fodg_file_size_div_20(_MINIMAL) == 73

    def test_exact_81_for_shapes(self):
        # shapes-basic: sz=1628 → 1628//20 = 81
        assert fodg_file_size_div_20(_SHAPES) == 81

    def test_positive(self):
        assert fodg_file_size_div_20(_EMPTY) > 0

    def test_consistent(self):
        assert fodg_file_size_div_20(_SHAPES) == fodg_file_size_div_20(_SHAPES)


class TestFodgShapeCountSquaredPlusPageCountTimes10:
    def test_return_type(self):
        assert isinstance(fodg_shape_count_squared_plus_page_count_times_10(_EMPTY), int)

    def test_exact_10_for_empty(self):
        # empty-page: sc=0, pg=1 → 0*0 + 1*10 = 10
        assert fodg_shape_count_squared_plus_page_count_times_10(_EMPTY) == 10

    def test_exact_11_for_minimal(self):
        # minimal-drawing: sc=1, pg=1 → 1*1 + 1*10 = 11
        assert fodg_shape_count_squared_plus_page_count_times_10(_MINIMAL) == 11

    def test_exact_19_for_shapes(self):
        # shapes-basic: sc=3, pg=1 → 3*3 + 1*10 = 19
        assert fodg_shape_count_squared_plus_page_count_times_10(_SHAPES) == 19

    def test_nonnegative(self):
        assert fodg_shape_count_squared_plus_page_count_times_10(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_shape_count_squared_plus_page_count_times_10(_SHAPES) == fodg_shape_count_squared_plus_page_count_times_10(_SHAPES)
