"""Tests for fodg_min_shape_count and fodg_is_empty_drawing (Sprint r301)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import fodg_min_shape_count, fodg_is_empty_drawing

_FODG = _REPO / "samples" / "by-format" / "fodg"


class TestFodgMinShapeCount:
    """Tests for fodg_min_shape_count."""

    def test_empty_page_has_min_zero(self):
        """empty-page.fodg has 0 shapes on all pages → min=0."""
        result = fodg_min_shape_count(_FODG / "empty-page.fodg")
        assert result == 0

    def test_minimal_drawing_has_min_one(self):
        """minimal-drawing.fodg has 1 shape → min=1."""
        result = fodg_min_shape_count(_FODG / "minimal-drawing.fodg")
        assert result == 1

    def test_shapes_basic_has_min_three(self):
        """shapes-basic.fodg has 3 shapes on its single page → min=3."""
        result = fodg_min_shape_count(_FODG / "shapes-basic.fodg")
        assert result == 3

    def test_returns_int(self):
        result = fodg_min_shape_count(_FODG / "minimal-drawing.fodg")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["empty-page.fodg", "minimal-drawing.fodg", "shapes-basic.fodg"]:
            assert fodg_min_shape_count(_FODG / f) >= 0

    def test_shapes_basic_min_more_than_minimal(self):
        r1 = fodg_min_shape_count(_FODG / "minimal-drawing.fodg")
        r2 = fodg_min_shape_count(_FODG / "shapes-basic.fodg")
        assert r2 > r1


class TestFodgIsEmptyDrawing:
    """Tests for fodg_is_empty_drawing."""

    def test_empty_page_is_empty_drawing(self):
        """empty-page.fodg has no shapes → True."""
        result = fodg_is_empty_drawing(_FODG / "empty-page.fodg")
        assert result is True

    def test_minimal_drawing_is_not_empty(self):
        """minimal-drawing.fodg has 1 shape → False."""
        result = fodg_is_empty_drawing(_FODG / "minimal-drawing.fodg")
        assert result is False

    def test_shapes_basic_is_not_empty(self):
        """shapes-basic.fodg has 3 shapes → False."""
        result = fodg_is_empty_drawing(_FODG / "shapes-basic.fodg")
        assert result is False

    def test_returns_bool(self):
        result = fodg_is_empty_drawing(_FODG / "empty-page.fodg")
        assert isinstance(result, bool)

    def test_non_empty_drawings_return_false(self):
        for f in ["minimal-drawing.fodg", "shapes-basic.fodg"]:
            assert fodg_is_empty_drawing(_FODG / f) is False

    def test_empty_true_minimal_false(self):
        r1 = fodg_is_empty_drawing(_FODG / "empty-page.fodg")
        r2 = fodg_is_empty_drawing(_FODG / "minimal-drawing.fodg")
        assert r1 is True and r2 is False
