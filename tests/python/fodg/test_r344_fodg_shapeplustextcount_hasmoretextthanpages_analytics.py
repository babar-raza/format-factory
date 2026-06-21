"""
Sprint r344: fodg_shape_plus_text_count + fodg_has_more_text_than_pages.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_shape_plus_text_count,
    fodg_has_more_text_than_pages,
)

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES = _FODG / "shapes-basic.fodg"


# fodg_shape_plus_text_count — empty=0, minimal=2, shapes-basic=5
def test_shape_plus_text_count_empty():
    assert fodg_shape_plus_text_count(_EMPTY) == 0

def test_shape_plus_text_count_minimal():
    assert fodg_shape_plus_text_count(_MINIMAL) == 2

def test_shape_plus_text_count_shapes():
    assert fodg_shape_plus_text_count(_SHAPES) == 5

def test_shape_plus_text_count_type():
    assert isinstance(fodg_shape_plus_text_count(_EMPTY), int)

def test_shape_plus_text_count_nonnegative():
    for p in (_EMPTY, _MINIMAL, _SHAPES):
        assert fodg_shape_plus_text_count(p) >= 0

def test_shape_plus_text_count_ordering():
    assert (fodg_shape_plus_text_count(_EMPTY) <
            fodg_shape_plus_text_count(_MINIMAL) <
            fodg_shape_plus_text_count(_SHAPES))


# fodg_has_more_text_than_pages — empty=False, minimal=False, shapes-basic=True
def test_has_more_text_than_pages_empty():
    assert fodg_has_more_text_than_pages(_EMPTY) is False

def test_has_more_text_than_pages_minimal():
    assert fodg_has_more_text_than_pages(_MINIMAL) is False

def test_has_more_text_than_pages_shapes():
    assert fodg_has_more_text_than_pages(_SHAPES) is True

def test_has_more_text_than_pages_type_empty():
    assert isinstance(fodg_has_more_text_than_pages(_EMPTY), bool)

def test_has_more_text_than_pages_type_shapes():
    assert isinstance(fodg_has_more_text_than_pages(_SHAPES), bool)

def test_has_more_text_than_pages_false_for_empty():
    result = fodg_has_more_text_than_pages(_EMPTY)
    assert result is False
