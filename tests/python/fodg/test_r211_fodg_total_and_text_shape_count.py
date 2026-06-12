"""
Tests for fodg_total_shape_count and fodg_text_shape_count — sprint product-deepening-rnext80.

Sprint: FORMAT-FACTORY-ABW-ZST-DEEPENING-001
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FODG_SAMPLES = REPO / "samples" / "by-format" / "fodg"

sys.path.insert(0, str(REPO / "src" / "python"))

from fodg.fodg_codec import fodg_total_shape_count, fodg_text_shape_count


def test_import_total():
    assert callable(fodg_total_shape_count)


def test_empty_page_has_no_shapes():
    result = fodg_total_shape_count(FODG_SAMPLES / "empty-page.fodg")
    assert result == 0


def test_minimal_drawing_has_one_shape():
    result = fodg_total_shape_count(FODG_SAMPLES / "minimal-drawing.fodg")
    assert result == 1


def test_shapes_basic_has_three_shapes():
    result = fodg_total_shape_count(FODG_SAMPLES / "shapes-basic.fodg")
    assert result == 3


def test_import_text():
    assert callable(fodg_text_shape_count)


def test_empty_page_has_no_text_shapes():
    result = fodg_text_shape_count(FODG_SAMPLES / "empty-page.fodg")
    assert result == 0


def test_minimal_drawing_has_one_text_shape():
    result = fodg_text_shape_count(FODG_SAMPLES / "minimal-drawing.fodg")
    assert result == 1


def test_shapes_basic_text_shape_count():
    result = fodg_text_shape_count(FODG_SAMPLES / "shapes-basic.fodg")
    assert result == 1


def test_total_returns_int():
    result = fodg_total_shape_count(FODG_SAMPLES / "empty-page.fodg")
    assert isinstance(result, int)


def test_text_returns_int():
    result = fodg_text_shape_count(FODG_SAMPLES / "minimal-drawing.fodg")
    assert isinstance(result, int)


def test_total_nonnegative():
    result = fodg_total_shape_count(FODG_SAMPLES / "empty-page.fodg")
    assert result >= 0


def test_text_nonnegative():
    result = fodg_text_shape_count(FODG_SAMPLES / "empty-page.fodg")
    assert result >= 0
