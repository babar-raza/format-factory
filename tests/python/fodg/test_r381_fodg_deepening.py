"""Tests for FODG product deepening sprint 152.

New functions:
  fodg_text_item_length_sum  — sum of char lengths of all text_content items
  fodg_shape_count_times_two — total shape count * 2
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import fodg_text_item_length_sum, fodg_shape_count_times_two

_EMPTY = str(_REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg")
_MIN = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
_SHP = str(_REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg")


class TestFodgTextItemLengthSum:
    def test_return_type(self):
        assert isinstance(fodg_text_item_length_sum(_EMPTY), int)

    def test_zero_for_empty_page(self):
        assert fodg_text_item_length_sum(_EMPTY) == 0

    def test_exact_9_for_minimal(self):
        # minimal-drawing: "Rectangle" (9 chars) → sum = 9
        assert fodg_text_item_length_sum(_MIN) == 9

    def test_exact_11_for_shapes_basic(self):
        # shapes-basic: "Rect" (4) + "Ellipse" (7) → sum = 11
        assert fodg_text_item_length_sum(_SHP) == 11

    def test_nonnegative(self):
        assert fodg_text_item_length_sum(_MIN) >= 0

    def test_consistent(self):
        assert fodg_text_item_length_sum(_SHP) == fodg_text_item_length_sum(_SHP)


class TestFodgShapeCountTimesTwo:
    def test_return_type(self):
        assert isinstance(fodg_shape_count_times_two(_EMPTY), int)

    def test_zero_for_empty_page(self):
        # empty-page: 0 shapes → 0 * 2 = 0
        assert fodg_shape_count_times_two(_EMPTY) == 0

    def test_exact_2_for_minimal(self):
        # minimal-drawing: 1 shape → 1 * 2 = 2
        assert fodg_shape_count_times_two(_MIN) == 2

    def test_exact_6_for_shapes_basic(self):
        # shapes-basic: 3 shapes → 3 * 2 = 6
        assert fodg_shape_count_times_two(_SHP) == 6

    def test_nonnegative(self):
        assert fodg_shape_count_times_two(_MIN) >= 0

    def test_consistent(self):
        assert fodg_shape_count_times_two(_SHP) == fodg_shape_count_times_two(_SHP)
