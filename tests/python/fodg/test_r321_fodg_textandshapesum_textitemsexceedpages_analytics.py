"""
r321 FODG analytics: fodg_text_and_shape_sum, fodg_text_items_exceed_pages.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg import fodg_text_and_shape_sum, fodg_text_items_exceed_pages

_FODG = _REPO / "samples" / "by-format" / "fodg"


# --- fodg_text_and_shape_sum ---

def test_text_and_shape_sum_empty_page():
    assert fodg_text_and_shape_sum(_FODG / "empty-page.fodg") == 0

def test_text_and_shape_sum_minimal_drawing():
    assert fodg_text_and_shape_sum(_FODG / "minimal-drawing.fodg") == 2

def test_text_and_shape_sum_shapes_basic():
    assert fodg_text_and_shape_sum(_FODG / "shapes-basic.fodg") == 5

def test_text_and_shape_sum_returns_int():
    result = fodg_text_and_shape_sum(_FODG / "empty-page.fodg")
    assert isinstance(result, int)

def test_text_and_shape_sum_shapes_greater_than_minimal():
    assert fodg_text_and_shape_sum(_FODG / "shapes-basic.fodg") > fodg_text_and_shape_sum(_FODG / "minimal-drawing.fodg")

def test_text_and_shape_sum_all_distinct():
    results = [
        fodg_text_and_shape_sum(_FODG / "empty-page.fodg"),
        fodg_text_and_shape_sum(_FODG / "minimal-drawing.fodg"),
        fodg_text_and_shape_sum(_FODG / "shapes-basic.fodg"),
    ]
    assert len(set(results)) == 3


# --- fodg_text_items_exceed_pages ---

def test_text_items_exceed_pages_empty_page_false():
    assert fodg_text_items_exceed_pages(_FODG / "empty-page.fodg") is False

def test_text_items_exceed_pages_minimal_drawing_false():
    assert fodg_text_items_exceed_pages(_FODG / "minimal-drawing.fodg") is False

def test_text_items_exceed_pages_shapes_basic_true():
    assert fodg_text_items_exceed_pages(_FODG / "shapes-basic.fodg") is True

def test_text_items_exceed_pages_returns_bool():
    result = fodg_text_items_exceed_pages(_FODG / "empty-page.fodg")
    assert isinstance(result, bool)

def test_text_items_exceed_pages_minimal_is_bool():
    result = fodg_text_items_exceed_pages(_FODG / "minimal-drawing.fodg")
    assert isinstance(result, bool)

def test_text_items_exceed_pages_only_shapes_true():
    results = [
        fodg_text_items_exceed_pages(_FODG / "empty-page.fodg"),
        fodg_text_items_exceed_pages(_FODG / "minimal-drawing.fodg"),
        fodg_text_items_exceed_pages(_FODG / "shapes-basic.fodg"),
    ]
    assert results.count(True) == 1
