"""Tests for FODG product deepening sprint 136.

New functions:
  fodg_text_item_length_range  — range of text item lengths (max - min)
  fodg_text_items_per_shape    — average text items per shape
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import fodg_text_item_length_range, fodg_text_items_per_shape

_MIN = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
_SHP = str(_REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg")
_EMP = str(_REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg")


class TestFodgTextItemLengthRange:
    def test_return_type(self):
        assert isinstance(fodg_text_item_length_range(_MIN), int)

    def test_zero_for_single_item(self):
        # minimal-drawing has 1 text item — range is 0
        assert fodg_text_item_length_range(_MIN) == 0

    def test_exact_3_for_shapes_basic(self):
        # shapes-basic: "Rect" (4) and "Ellipse" (7) -> range = 3
        assert fodg_text_item_length_range(_SHP) == 3

    def test_zero_for_empty_page(self):
        assert fodg_text_item_length_range(_EMP) == 0

    def test_nonnegative(self):
        assert fodg_text_item_length_range(_SHP) >= 0

    def test_consistent(self):
        assert fodg_text_item_length_range(_SHP) == fodg_text_item_length_range(_SHP)


class TestFodgTextItemsPerShape:
    def test_return_type(self):
        assert isinstance(fodg_text_items_per_shape(_MIN), float)

    def test_exact_1_0_for_minimal(self):
        # minimal-drawing: 1 text item / 1 shape = 1.0
        assert fodg_text_items_per_shape(_MIN) == 1.0

    def test_exact_ratio_for_shapes_basic(self):
        # shapes-basic: 2 text items / 3 shapes ≈ 0.6667
        result = fodg_text_items_per_shape(_SHP)
        assert abs(result - 2 / 3) < 1e-9

    def test_zero_for_empty_page(self):
        # empty-page has no shapes
        assert fodg_text_items_per_shape(_EMP) == 0.0

    def test_nonnegative(self):
        assert fodg_text_items_per_shape(_MIN) >= 0.0

    def test_consistent(self):
        assert fodg_text_items_per_shape(_SHP) == fodg_text_items_per_shape(_SHP)
