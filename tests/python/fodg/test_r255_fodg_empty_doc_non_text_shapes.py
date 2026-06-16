"""Tests for fodg_is_empty_document and fodg_non_text_shape_count (Sprint 45)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import fodg_is_empty_document, fodg_non_text_shape_count

_DIR = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = str(_DIR / "empty-page.fodg")      # 0 shapes: is_empty=True, non_text=0
_MINIMAL = str(_DIR / "minimal-drawing.fodg") # 1 text shape: is_empty=False, non_text=0
_SHAPES = str(_DIR / "shapes-basic.fodg")    # 3 shapes (1 text, 2 non-text): is_empty=F, non_text=2


class TestFodgIsEmptyDocument:
    def test_return_type(self):
        assert isinstance(fodg_is_empty_document(_EMPTY), bool)

    def test_true_for_empty_page(self):
        # empty-page.fodg: 0 shapes -> is_empty=True
        assert fodg_is_empty_document(_EMPTY) is True

    def test_false_for_minimal_drawing(self):
        # minimal-drawing.fodg: 1 shape -> is_empty=False
        assert fodg_is_empty_document(_MINIMAL) is False

    def test_false_for_shapes_basic(self):
        # shapes-basic.fodg: 3 shapes -> is_empty=False
        assert fodg_is_empty_document(_SHAPES) is False

    def test_consistent_across_calls(self):
        assert fodg_is_empty_document(_EMPTY) == fodg_is_empty_document(_EMPTY)

    def test_true_is_not_none(self):
        result = fodg_is_empty_document(_EMPTY)
        assert result is True
        assert result is not None


class TestFodgNonTextShapeCount:
    def test_return_type(self):
        assert isinstance(fodg_non_text_shape_count(_EMPTY), int)

    def test_exact_0_for_empty(self):
        # empty-page.fodg: 0 total, 0 text -> non_text=0
        assert fodg_non_text_shape_count(_EMPTY) == 0

    def test_exact_0_for_minimal(self):
        # minimal-drawing.fodg: 1 total, 1 text -> non_text=0
        assert fodg_non_text_shape_count(_MINIMAL) == 0

    def test_exact_2_for_shapes_basic(self):
        # shapes-basic.fodg: 3 total, 1 text -> non_text=2
        assert fodg_non_text_shape_count(_SHAPES) == 2

    def test_nonnegative(self):
        assert fodg_non_text_shape_count(_SHAPES) >= 0

    def test_consistent_across_calls(self):
        assert fodg_non_text_shape_count(_SHAPES) == fodg_non_text_shape_count(_SHAPES)
