"""Tests for fodg_total_text_items and fodg_avg_shapes_per_page (Sprint 65)."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "python"))

from fodg.fodg_codec import fodg_total_text_items, fodg_avg_shapes_per_page

FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"


class TestFodgTotalTextItems:
    def test_minimal(self):
        assert fodg_total_text_items(FODG / "minimal-drawing.fodg") == 1

    def test_shapes_basic(self):
        assert fodg_total_text_items(FODG / "shapes-basic.fodg") == 2

    def test_empty_page(self):
        assert fodg_total_text_items(FODG / "empty-page.fodg") == 0

    def test_returns_int(self):
        assert isinstance(fodg_total_text_items(FODG / "minimal-drawing.fodg"), int)

    def test_nonnegative(self):
        for f in ["minimal-drawing.fodg", "shapes-basic.fodg", "empty-page.fodg"]:
            assert fodg_total_text_items(FODG / f) >= 0


class TestFodgAvgShapesPerPage:
    def test_minimal(self):
        assert abs(fodg_avg_shapes_per_page(FODG / "minimal-drawing.fodg") - 1.0) < 0.01

    def test_shapes_basic(self):
        assert abs(fodg_avg_shapes_per_page(FODG / "shapes-basic.fodg") - 3.0) < 0.01

    def test_empty_page(self):
        assert fodg_avg_shapes_per_page(FODG / "empty-page.fodg") == 0.0

    def test_returns_float(self):
        assert isinstance(fodg_avg_shapes_per_page(FODG / "minimal-drawing.fodg"), float)

    def test_nonnegative(self):
        for f in ["minimal-drawing.fodg", "shapes-basic.fodg", "empty-page.fodg"]:
            assert fodg_avg_shapes_per_page(FODG / f) >= 0.0
