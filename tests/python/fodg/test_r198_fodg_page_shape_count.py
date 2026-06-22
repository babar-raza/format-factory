"""
Tests for fodg_page_shape_count — sprint product-deepening-rnext67.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FODG_SAMPLES = REPO / "samples" / "by-format" / "fodg"

sys.path.insert(0, str(REPO / "src" / "python"))

from fodg import load, fodg_page_shape_count


def test_import():
    assert callable(fodg_page_shape_count)


def test_shapes_basic_has_three_shapes():
    model = load(FODG_SAMPLES / "shapes-basic.fodg")
    result = fodg_page_shape_count(model, 0)
    assert result == 3


def test_minimal_drawing_has_one_shape():
    model = load(FODG_SAMPLES / "minimal-drawing.fodg")
    result = fodg_page_shape_count(model, 0)
    assert result == 1


def test_empty_page_returns_zero():
    model = load(FODG_SAMPLES / "empty-page.fodg")
    result = fodg_page_shape_count(model, 0)
    assert result == 0


def test_out_of_range_returns_zero():
    model = load(FODG_SAMPLES / "shapes-basic.fodg")
    result = fodg_page_shape_count(model, 99)
    assert result == 0


def test_returns_int():
    model = load(FODG_SAMPLES / "shapes-basic.fodg")
    result = fodg_page_shape_count(model, 0)
    assert isinstance(result, int)
