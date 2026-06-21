"""
Sprint r347: fodg_total_shape_count_squared + fodg_has_at_least_two_text_items.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_total_shape_count_squared,
    fodg_has_at_least_two_text_items,
)

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES = _FODG / "shapes-basic.fodg"


# fodg_total_shape_count_squared — empty=0, minimal=1, shapes-basic=9
def test_total_shape_count_squared_empty():
    assert fodg_total_shape_count_squared(_EMPTY) == 0

def test_total_shape_count_squared_minimal():
    assert fodg_total_shape_count_squared(_MINIMAL) == 1

def test_total_shape_count_squared_shapes():
    assert fodg_total_shape_count_squared(_SHAPES) == 9

def test_total_shape_count_squared_type():
    assert isinstance(fodg_total_shape_count_squared(_EMPTY), int)

def test_total_shape_count_squared_nonnegative():
    for p in (_EMPTY, _MINIMAL, _SHAPES):
        assert fodg_total_shape_count_squared(p) >= 0

def test_total_shape_count_squared_ordering():
    assert (fodg_total_shape_count_squared(_EMPTY) <
            fodg_total_shape_count_squared(_MINIMAL) <
            fodg_total_shape_count_squared(_SHAPES))


# fodg_has_at_least_two_text_items — empty=False, minimal=False, shapes-basic=True
def test_has_at_least_two_text_items_empty():
    assert fodg_has_at_least_two_text_items(_EMPTY) is False

def test_has_at_least_two_text_items_minimal():
    assert fodg_has_at_least_two_text_items(_MINIMAL) is False

def test_has_at_least_two_text_items_shapes():
    assert fodg_has_at_least_two_text_items(_SHAPES) is True

def test_has_at_least_two_text_items_type_empty():
    assert isinstance(fodg_has_at_least_two_text_items(_EMPTY), bool)

def test_has_at_least_two_text_items_type_shapes():
    assert isinstance(fodg_has_at_least_two_text_items(_SHAPES), bool)

def test_has_at_least_two_text_items_false_for_minimal():
    result = fodg_has_at_least_two_text_items(_MINIMAL)
    assert result is False
