"""Tests for r329 rework: FODG analytics functions.

Functions:
  fodg_page_count_plus_shape_count  — page count + total shape count
  fodg_shape_count_equals_page_count — True if total shapes == page count
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_page_count_plus_shape_count,
    fodg_shape_count_equals_page_count,
)

_EMPTY = str(_REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg")
_MIN = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
_SHP = str(_REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg")


class TestFodgPageCountPlusShapeCount:
    def test_return_type(self):
        assert isinstance(fodg_page_count_plus_shape_count(_EMPTY), int)

    def test_exact_1_for_empty_page(self):
        # empty-page: 1 page + 0 shapes = 1
        assert fodg_page_count_plus_shape_count(_EMPTY) == 1

    def test_exact_2_for_minimal(self):
        # minimal-drawing: 1 page + 1 shape = 2
        assert fodg_page_count_plus_shape_count(_MIN) == 2

    def test_exact_4_for_shapes_basic(self):
        # shapes-basic: 1 page + 3 shapes = 4
        assert fodg_page_count_plus_shape_count(_SHP) == 4

    def test_positive(self):
        assert fodg_page_count_plus_shape_count(_MIN) >= 1

    def test_consistent(self):
        assert fodg_page_count_plus_shape_count(_SHP) == fodg_page_count_plus_shape_count(_SHP)


class TestFodgShapeCountEqualsPageCount:
    def test_return_type(self):
        assert isinstance(fodg_shape_count_equals_page_count(_EMPTY), bool)

    def test_false_for_empty_page(self):
        # empty-page: 0 shapes != 1 page
        assert fodg_shape_count_equals_page_count(_EMPTY) is False

    def test_true_for_minimal(self):
        # minimal-drawing: 1 shape == 1 page
        assert fodg_shape_count_equals_page_count(_MIN) is True

    def test_false_for_shapes_basic(self):
        # shapes-basic: 3 shapes != 1 page
        assert fodg_shape_count_equals_page_count(_SHP) is False

    def test_consistent(self):
        assert fodg_shape_count_equals_page_count(_MIN) == fodg_shape_count_equals_page_count(_MIN)
