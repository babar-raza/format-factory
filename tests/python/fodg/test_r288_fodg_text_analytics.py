"""
Tests for FODG additional text analytics (2 new FOSS functions).
Closes: GAP-FODG-FOSS-FODG_ALL_PAG-001, GAP-FODG-FOSS-FODG_MAX_TEX-001

Known sample values (from fodg_all_pages_have_text / fodg_max_text_item_length):
  empty-page.fodg:     all_pages_have_text=False, max_text_item_length=0
  minimal-drawing.fodg: all_pages_have_text=True,  max_text_item_length=9  ("Rectangle")
  shapes-basic.fodg:   all_pages_have_text=True,  max_text_item_length=7  ("Ellipse")
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg import fodg_all_pages_have_text, fodg_max_text_item_length

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES = _FODG / "shapes-basic.fodg"


class TestFodgAllPagesHaveText:
    def test_returns_bool(self):
        assert isinstance(fodg_all_pages_have_text(_EMPTY), bool)

    def test_empty_page_is_false(self):
        # empty-page has no text content
        assert fodg_all_pages_have_text(_EMPTY) is False

    def test_minimal_drawing_is_true(self):
        # minimal-drawing has "Rectangle" text
        assert fodg_all_pages_have_text(_MINIMAL) is True

    def test_shapes_basic_is_true(self):
        # shapes-basic has ["Rect", "Ellipse"] text
        assert fodg_all_pages_have_text(_SHAPES) is True

    def test_empty_differs_from_shapes(self):
        assert fodg_all_pages_have_text(_EMPTY) is not fodg_all_pages_have_text(_SHAPES)

    def test_all_return_bool(self):
        for p in [_EMPTY, _MINIMAL, _SHAPES]:
            assert isinstance(fodg_all_pages_have_text(p), bool)


class TestFodgMaxTextItemLength:
    def test_returns_int(self):
        assert isinstance(fodg_max_text_item_length(_EMPTY), int)

    def test_empty_page_returns_zero(self):
        assert fodg_max_text_item_length(_EMPTY) == 0

    def test_minimal_drawing_returns_nine(self):
        # "Rectangle" = 9 chars
        assert fodg_max_text_item_length(_MINIMAL) == 9

    def test_shapes_basic_returns_seven(self):
        # "Ellipse" = 7 chars (longer than "Rect" = 4)
        assert fodg_max_text_item_length(_SHAPES) == 7

    def test_nonnegative(self):
        for p in [_EMPTY, _MINIMAL, _SHAPES]:
            assert fodg_max_text_item_length(p) >= 0

    def test_empty_lower_than_minimal(self):
        assert fodg_max_text_item_length(_EMPTY) < fodg_max_text_item_length(_MINIMAL)

    def test_all_return_int(self):
        for p in [_EMPTY, _MINIMAL, _SHAPES]:
            assert isinstance(fodg_max_text_item_length(p), int)
