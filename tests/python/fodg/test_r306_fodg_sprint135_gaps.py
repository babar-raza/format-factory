"""Tests for FODG Sprint 135 gap closure.

Closes:
  GAP-FODG-FOSS-FODG_TEXT_AN-001   (Fodg Text And Shape Sum)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import fodg_text_and_shape_sum

_DIR = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = str(_DIR / "empty-page.fodg")
_MINIMAL = str(_DIR / "minimal-drawing.fodg")
_SHAPES = str(_DIR / "shapes-basic.fodg")


class TestFodgTextAndShapeSum:
    def test_return_type(self):
        assert isinstance(fodg_text_and_shape_sum(_EMPTY), int)

    def test_exact_0_for_empty(self):
        assert fodg_text_and_shape_sum(_EMPTY) == 0

    def test_exact_2_for_minimal(self):
        assert fodg_text_and_shape_sum(_MINIMAL) == 2

    def test_exact_5_for_shapes(self):
        assert fodg_text_and_shape_sum(_SHAPES) == 5

    def test_nonnegative(self):
        assert fodg_text_and_shape_sum(_EMPTY) >= 0

    def test_consistent(self):
        assert fodg_text_and_shape_sum(_MINIMAL) == fodg_text_and_shape_sum(_MINIMAL)
