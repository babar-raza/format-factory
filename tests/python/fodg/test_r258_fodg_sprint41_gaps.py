"""Tests for FODG Sprint 41 gap closure.

Closes:
  GAP-FODG-FOSS-FODG_HAS_NO-001  (Fodg Has Non Text Shapes)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import fodg_has_non_text_shapes

_DIR = _REPO / "samples" / "by-format" / "fodg"
_EMPTY_PAGE = str(_DIR / "empty-page.fodg")
_MINIMAL_DRAWING = str(_DIR / "minimal-drawing.fodg")
_SHAPES_BASIC = str(_DIR / "shapes-basic.fodg")


class TestFodgHasNonTextShapes:
    def test_return_type(self):
        assert isinstance(fodg_has_non_text_shapes(_EMPTY_PAGE), bool)

    def test_false_for_empty_page(self):
        assert fodg_has_non_text_shapes(_EMPTY_PAGE) is False

    def test_false_for_minimal_drawing(self):
        assert fodg_has_non_text_shapes(_MINIMAL_DRAWING) is False

    def test_true_for_shapes_basic(self):
        assert fodg_has_non_text_shapes(_SHAPES_BASIC) is True

    def test_consistent_across_calls(self):
        assert fodg_has_non_text_shapes(_SHAPES_BASIC) == fodg_has_non_text_shapes(_SHAPES_BASIC)
