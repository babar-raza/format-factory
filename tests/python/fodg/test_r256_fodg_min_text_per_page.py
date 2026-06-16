"""Tests for fodg_min_text_per_page (Sprint 40).

Closes:
  GAP-FODG-FOSS-FODG_MIN_TEX-001  (Fodg Min Text Per Page)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import fodg_min_text_per_page

_DIR = _REPO / "samples" / "by-format" / "fodg"
_EMPTY_PAGE = str(_DIR / "empty-page.fodg")
_MINIMAL_DRAWING = str(_DIR / "minimal-drawing.fodg")
_SHAPES_BASIC = str(_DIR / "shapes-basic.fodg")


class TestFodgMinTextPerPage:
    def test_return_type(self):
        assert isinstance(fodg_min_text_per_page(_EMPTY_PAGE), int)

    def test_zero_for_empty_page(self):
        assert fodg_min_text_per_page(_EMPTY_PAGE) == 0

    def test_zero_for_minimal_drawing(self):
        assert fodg_min_text_per_page(_MINIMAL_DRAWING) == 0

    def test_zero_for_shapes_basic(self):
        assert fodg_min_text_per_page(_SHAPES_BASIC) == 0

    def test_nonnegative(self):
        assert fodg_min_text_per_page(_EMPTY_PAGE) >= 0

    def test_consistent_across_calls(self):
        assert fodg_min_text_per_page(_EMPTY_PAGE) == fodg_min_text_per_page(_EMPTY_PAGE)
