"""Tests for FODG Sprint 142 gap closure.

Closes:
  GAP-FODG-FOSS-FODG_HAS_EQU-001  (Fodg Has Equal Shapes And Text)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import fodg_has_equal_shapes_and_text

_MIN = str(_REPO / "samples" / "by-format" / "fodg" / "minimal-drawing.fodg")
_SHP = str(_REPO / "samples" / "by-format" / "fodg" / "shapes-basic.fodg")
_EMP = str(_REPO / "samples" / "by-format" / "fodg" / "empty-page.fodg")


class TestFodgHasEqualShapesAndText:
    def test_return_type(self):
        assert isinstance(fodg_has_equal_shapes_and_text(_MIN), bool)

    def test_true_for_minimal(self):
        # minimal-drawing: 1 shape, 1 text item → equal
        assert fodg_has_equal_shapes_and_text(_MIN) is True

    def test_false_for_shapes_basic(self):
        # shapes-basic: 3 shapes, 2 text items → not equal
        assert fodg_has_equal_shapes_and_text(_SHP) is False

    def test_true_for_empty_page(self):
        # empty-page: 0 shapes, 0 text items → equal (both zero)
        assert fodg_has_equal_shapes_and_text(_EMP) is True

    def test_consistent(self):
        assert fodg_has_equal_shapes_and_text(_SHP) == fodg_has_equal_shapes_and_text(_SHP)
