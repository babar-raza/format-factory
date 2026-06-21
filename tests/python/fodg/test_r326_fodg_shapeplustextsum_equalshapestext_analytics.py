"""
r326 FODG analytics: fodg_total_shape_count_plus_text_item_count, fodg_has_equal_shapes_and_text.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import fodg_total_shape_count_plus_text_item_count, fodg_has_equal_shapes_and_text

_FODG = _REPO / "samples" / "by-format" / "fodg"


# --- fodg_total_shape_count_plus_text_item_count ---

def test_shape_plus_text_empty():
    assert fodg_total_shape_count_plus_text_item_count(_FODG / "empty-page.fodg") == 0

def test_shape_plus_text_minimal():
    assert fodg_total_shape_count_plus_text_item_count(_FODG / "minimal-drawing.fodg") == 2

def test_shape_plus_text_shapes():
    assert fodg_total_shape_count_plus_text_item_count(_FODG / "shapes-basic.fodg") == 5

def test_shape_plus_text_returns_int():
    result = fodg_total_shape_count_plus_text_item_count(_FODG / "empty-page.fodg")
    assert isinstance(result, int)

def test_shape_plus_text_nonnegative():
    for f in ["empty-page.fodg", "minimal-drawing.fodg", "shapes-basic.fodg"]:
        assert fodg_total_shape_count_plus_text_item_count(_FODG / f) >= 0

def test_shape_plus_text_all_distinct():
    results = [
        fodg_total_shape_count_plus_text_item_count(_FODG / "empty-page.fodg"),
        fodg_total_shape_count_plus_text_item_count(_FODG / "minimal-drawing.fodg"),
        fodg_total_shape_count_plus_text_item_count(_FODG / "shapes-basic.fodg"),
    ]
    assert len(set(results)) == 3


# --- fodg_has_equal_shapes_and_text ---

def test_equal_shapes_text_empty_true():
    assert fodg_has_equal_shapes_and_text(_FODG / "empty-page.fodg") is True

def test_equal_shapes_text_minimal_true():
    assert fodg_has_equal_shapes_and_text(_FODG / "minimal-drawing.fodg") is True

def test_equal_shapes_text_shapes_false():
    assert fodg_has_equal_shapes_and_text(_FODG / "shapes-basic.fodg") is False

def test_equal_shapes_text_returns_bool():
    result = fodg_has_equal_shapes_and_text(_FODG / "empty-page.fodg")
    assert isinstance(result, bool)

def test_equal_shapes_text_minimal_is_bool():
    result = fodg_has_equal_shapes_and_text(_FODG / "minimal-drawing.fodg")
    assert isinstance(result, bool)

def test_equal_shapes_text_only_shapes_false():
    results = [
        fodg_has_equal_shapes_and_text(_FODG / "empty-page.fodg"),
        fodg_has_equal_shapes_and_text(_FODG / "minimal-drawing.fodg"),
        fodg_has_equal_shapes_and_text(_FODG / "shapes-basic.fodg"),
    ]
    assert results.count(False) == 1
