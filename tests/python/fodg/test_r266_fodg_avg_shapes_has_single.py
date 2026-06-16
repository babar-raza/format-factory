"""Tests for fodg_avg_shapes_per_nonempty_page and fodg_has_single_shape (Sprint 56)."""
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from fodg.fodg_codec import fodg_avg_shapes_per_nonempty_page, fodg_has_single_shape

FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"


class TestFodgAvgShapesPerNonemptyPage:
    def test_minimal_drawing(self):
        assert fodg_avg_shapes_per_nonempty_page(FODG / "minimal-drawing.fodg") == 1.0

    def test_shapes_basic(self):
        assert fodg_avg_shapes_per_nonempty_page(FODG / "shapes-basic.fodg") == 3.0

    def test_empty_page(self):
        assert fodg_avg_shapes_per_nonempty_page(FODG / "empty-page.fodg") == 0.0

    def test_returns_float(self):
        result = fodg_avg_shapes_per_nonempty_page(FODG / "minimal-drawing.fodg")
        assert isinstance(result, float)

    def test_nonnegative(self):
        for f in ["minimal-drawing.fodg", "shapes-basic.fodg", "empty-page.fodg"]:
            assert fodg_avg_shapes_per_nonempty_page(FODG / f) >= 0.0


class TestFodgHasSingleShape:
    def test_minimal_drawing_has_single(self):
        assert fodg_has_single_shape(FODG / "minimal-drawing.fodg") is True

    def test_shapes_basic_not_single(self):
        assert fodg_has_single_shape(FODG / "shapes-basic.fodg") is False

    def test_empty_page_not_single(self):
        assert fodg_has_single_shape(FODG / "empty-page.fodg") is False

    def test_returns_bool(self):
        result = fodg_has_single_shape(FODG / "minimal-drawing.fodg")
        assert isinstance(result, bool)

    def test_false_for_multiple_shapes(self):
        assert fodg_has_single_shape(FODG / "shapes-basic.fodg") is False
