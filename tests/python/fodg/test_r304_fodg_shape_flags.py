"""Tests for fodg_has_multiple_shapes and fodg_shapes_exceed_pages (Sprint r304)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import fodg_has_multiple_shapes, fodg_shapes_exceed_pages

_FODG = _REPO / "samples" / "by-format" / "fodg"


class TestFodgHasMultipleShapes:
    """Tests for fodg_has_multiple_shapes."""

    def test_empty_page_no_multiple(self):
        """empty-page.fodg has 0 shapes → False."""
        assert fodg_has_multiple_shapes(_FODG / "empty-page.fodg") is False

    def test_minimal_drawing_no_multiple(self):
        """minimal-drawing.fodg has exactly 1 shape → False."""
        assert fodg_has_multiple_shapes(_FODG / "minimal-drawing.fodg") is False

    def test_shapes_basic_has_multiple(self):
        """shapes-basic.fodg has 3 shapes → True."""
        assert fodg_has_multiple_shapes(_FODG / "shapes-basic.fodg") is True

    def test_returns_bool(self):
        assert isinstance(fodg_has_multiple_shapes(_FODG / "shapes-basic.fodg"), bool)

    def test_empty_and_minimal_both_false(self):
        for f in ["empty-page.fodg", "minimal-drawing.fodg"]:
            assert fodg_has_multiple_shapes(_FODG / f) is False

    def test_basic_true_empty_false(self):
        r1 = fodg_has_multiple_shapes(_FODG / "shapes-basic.fodg")
        r2 = fodg_has_multiple_shapes(_FODG / "empty-page.fodg")
        assert r1 is True and r2 is False


class TestFodgShapesExceedPages:
    """Tests for fodg_shapes_exceed_pages."""

    def test_empty_page_shapes_not_exceed(self):
        """empty-page.fodg has 0 shapes, 1 page → False."""
        assert fodg_shapes_exceed_pages(_FODG / "empty-page.fodg") is False

    def test_minimal_drawing_shapes_not_exceed(self):
        """minimal-drawing.fodg has 1 shape, 1 page → False."""
        assert fodg_shapes_exceed_pages(_FODG / "minimal-drawing.fodg") is False

    def test_shapes_basic_exceeds(self):
        """shapes-basic.fodg has 3 shapes, 1 page → True."""
        assert fodg_shapes_exceed_pages(_FODG / "shapes-basic.fodg") is True

    def test_returns_bool(self):
        assert isinstance(fodg_shapes_exceed_pages(_FODG / "shapes-basic.fodg"), bool)

    def test_two_files_not_exceed(self):
        for f in ["empty-page.fodg", "minimal-drawing.fodg"]:
            assert fodg_shapes_exceed_pages(_FODG / f) is False

    def test_basic_exceeds_empty_does_not(self):
        r1 = fodg_shapes_exceed_pages(_FODG / "shapes-basic.fodg")
        r2 = fodg_shapes_exceed_pages(_FODG / "empty-page.fodg")
        assert r1 is True and r2 is False
