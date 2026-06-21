"""Tests for FODG product deepening sprint 154.

New functions:
  fodg_shape_count_times_text_count  — total shapes * total text items
  fodg_shape_plus_text_plus_page_count — shapes + text items + pages
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import (
    fodg_shape_count_times_text_count,
    fodg_shape_plus_text_plus_page_count,
)

_EMPTY = str(_REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg")
_MIN = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
_SHP = str(_REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg")


class TestFodgShapeCountTimesTextCount:
    def test_return_type(self):
        assert isinstance(fodg_shape_count_times_text_count(_EMPTY), int)

    def test_zero_for_empty_page(self):
        # empty-page: 0 shapes * 0 texts = 0
        assert fodg_shape_count_times_text_count(_EMPTY) == 0

    def test_exact_1_for_minimal(self):
        # minimal-drawing: 1 shape * 1 text = 1
        assert fodg_shape_count_times_text_count(_MIN) == 1

    def test_exact_6_for_shapes_basic(self):
        # shapes-basic: 3 shapes * 2 texts = 6
        assert fodg_shape_count_times_text_count(_SHP) == 6

    def test_nonnegative(self):
        assert fodg_shape_count_times_text_count(_MIN) >= 0

    def test_consistent(self):
        assert fodg_shape_count_times_text_count(_SHP) == fodg_shape_count_times_text_count(_SHP)


class TestFodgShapePlusTextPlusPageCount:
    def test_return_type(self):
        assert isinstance(fodg_shape_plus_text_plus_page_count(_EMPTY), int)

    def test_exact_1_for_empty_page(self):
        # empty-page: 0 shapes + 0 texts + 1 page = 1
        assert fodg_shape_plus_text_plus_page_count(_EMPTY) == 1

    def test_exact_3_for_minimal(self):
        # minimal-drawing: 1 shape + 1 text + 1 page = 3
        assert fodg_shape_plus_text_plus_page_count(_MIN) == 3

    def test_exact_6_for_shapes_basic(self):
        # shapes-basic: 3 shapes + 2 texts + 1 page = 6
        assert fodg_shape_plus_text_plus_page_count(_SHP) == 6

    def test_positive(self):
        # always at least 1 (page count)
        assert fodg_shape_plus_text_plus_page_count(_EMPTY) >= 1

    def test_consistent(self):
        assert fodg_shape_plus_text_plus_page_count(_SHP) == fodg_shape_plus_text_plus_page_count(_SHP)
