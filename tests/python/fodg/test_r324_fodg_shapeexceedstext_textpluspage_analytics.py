"""
r324 FODG analytics: fodg_shape_count_exceeds_text_count, fodg_text_item_count_plus_page_count.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import fodg_shape_count_exceeds_text_count, fodg_text_item_count_plus_page_count

_FODG = _REPO / "samples" / "by-format" / "fodg"


# --- fodg_shape_count_exceeds_text_count ---

def test_shape_exceeds_text_empty_false():
    assert fodg_shape_count_exceeds_text_count(_FODG / "empty-page.fodg") is False

def test_shape_exceeds_text_minimal_false():
    assert fodg_shape_count_exceeds_text_count(_FODG / "minimal-drawing.fodg") is False

def test_shape_exceeds_text_shapes_true():
    assert fodg_shape_count_exceeds_text_count(_FODG / "shapes-basic.fodg") is True

def test_shape_exceeds_text_returns_bool():
    result = fodg_shape_count_exceeds_text_count(_FODG / "empty-page.fodg")
    assert isinstance(result, bool)

def test_shape_exceeds_text_minimal_is_bool():
    result = fodg_shape_count_exceeds_text_count(_FODG / "minimal-drawing.fodg")
    assert isinstance(result, bool)

def test_shape_exceeds_text_only_shapes_true():
    results = [
        fodg_shape_count_exceeds_text_count(_FODG / "empty-page.fodg"),
        fodg_shape_count_exceeds_text_count(_FODG / "minimal-drawing.fodg"),
        fodg_shape_count_exceeds_text_count(_FODG / "shapes-basic.fodg"),
    ]
    assert results.count(True) == 1


# --- fodg_text_item_count_plus_page_count ---

def test_text_plus_page_empty():
    assert fodg_text_item_count_plus_page_count(_FODG / "empty-page.fodg") == 1

def test_text_plus_page_minimal():
    assert fodg_text_item_count_plus_page_count(_FODG / "minimal-drawing.fodg") == 2

def test_text_plus_page_shapes():
    assert fodg_text_item_count_plus_page_count(_FODG / "shapes-basic.fodg") == 3

def test_text_plus_page_returns_int():
    result = fodg_text_item_count_plus_page_count(_FODG / "empty-page.fodg")
    assert isinstance(result, int)

def test_text_plus_page_nonnegative():
    for f in ["empty-page.fodg", "minimal-drawing.fodg", "shapes-basic.fodg"]:
        assert fodg_text_item_count_plus_page_count(_FODG / f) >= 0

def test_text_plus_page_all_distinct():
    results = [
        fodg_text_item_count_plus_page_count(_FODG / "empty-page.fodg"),
        fodg_text_item_count_plus_page_count(_FODG / "minimal-drawing.fodg"),
        fodg_text_item_count_plus_page_count(_FODG / "shapes-basic.fodg"),
    ]
    assert len(set(results)) == 3
