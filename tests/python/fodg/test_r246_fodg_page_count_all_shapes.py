"""Tests for fodg_page_count and fodg_all_pages_have_shapes (Sprint 36)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import fodg_page_count, fodg_all_pages_have_shapes

_SAMPLES = _REPO / "samples" / "by-format" / "fodg"
_MINIMAL = str(_SAMPLES / "minimal-drawing.fodg")   # 1 page, 1 shape -> all_shapes=True
_EMPTY = str(_SAMPLES / "empty-page.fodg")           # 1 page, 0 shapes -> all_shapes=False
_SHAPES = str(_SAMPLES / "shapes-basic.fodg")        # 1 page, 3 shapes -> all_shapes=True


class TestFodgPageCount:
    def test_return_type(self):
        result = fodg_page_count(_MINIMAL)
        assert isinstance(result, int)

    def test_one_page_minimal(self):
        assert fodg_page_count(_MINIMAL) == 1

    def test_one_page_empty(self):
        assert fodg_page_count(_EMPTY) == 1

    def test_nonnegative(self):
        assert fodg_page_count(_SHAPES) >= 0

    def test_consistent_across_calls(self):
        assert fodg_page_count(_MINIMAL) == fodg_page_count(_MINIMAL)


class TestFodgAllPagesHaveShapes:
    def test_return_type(self):
        result = fodg_all_pages_have_shapes(_MINIMAL)
        assert isinstance(result, bool)

    def test_true_for_minimal_with_shape(self):
        assert fodg_all_pages_have_shapes(_MINIMAL) is True

    def test_false_for_empty_page(self):
        assert fodg_all_pages_have_shapes(_EMPTY) is False

    def test_true_for_shapes_basic(self):
        assert fodg_all_pages_have_shapes(_SHAPES) is True

    def test_consistent_across_calls(self):
        assert fodg_all_pages_have_shapes(_MINIMAL) == fodg_all_pages_have_shapes(_MINIMAL)
