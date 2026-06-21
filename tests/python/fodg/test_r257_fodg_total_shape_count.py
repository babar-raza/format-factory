"""Tests for fodg_total_shape_count (Sprint 40 batch 3).

Closes:
  GAP-FODG-FOSS-FODG_SHAPES_-001  (Fodg Shapes Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import fodg_total_shape_count

_DIR = _REPO / "samples" / "by-format" / "fodg"
_EMPTY_PAGE = str(_DIR / "empty-page.fodg")
_MINIMAL_DRAWING = str(_DIR / "minimal-drawing.fodg")
_SHAPES_BASIC = str(_DIR / "shapes-basic.fodg")


class TestFodgTotalShapeCount:
    def test_return_type(self):
        assert isinstance(fodg_total_shape_count(_EMPTY_PAGE), int)

    def test_zero_for_empty_page(self):
        assert fodg_total_shape_count(_EMPTY_PAGE) == 0

    def test_exact_1_for_minimal_drawing(self):
        assert fodg_total_shape_count(_MINIMAL_DRAWING) == 1

    def test_exact_3_for_shapes_basic(self):
        assert fodg_total_shape_count(_SHAPES_BASIC) == 3

    def test_nonnegative(self):
        assert fodg_total_shape_count(_EMPTY_PAGE) >= 0

    def test_consistent_across_calls(self):
        assert fodg_total_shape_count(_SHAPES_BASIC) == fodg_total_shape_count(_SHAPES_BASIC)
