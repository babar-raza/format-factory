"""
Sprint r346: fodg_shape_count_div_page_count + fodg_has_more_shapes_than_text.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_shape_count_div_page_count,
    fodg_has_more_shapes_than_text,
)

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES = _FODG / "shapes-basic.fodg"


# fodg_shape_count_div_page_count — empty=0, minimal=1, shapes-basic=3
def test_shape_count_div_page_count_empty():
    assert fodg_shape_count_div_page_count(_EMPTY) == 0

def test_shape_count_div_page_count_minimal():
    assert fodg_shape_count_div_page_count(_MINIMAL) == 1

def test_shape_count_div_page_count_shapes():
    assert fodg_shape_count_div_page_count(_SHAPES) == 3

def test_shape_count_div_page_count_type():
    assert isinstance(fodg_shape_count_div_page_count(_EMPTY), int)

def test_shape_count_div_page_count_nonnegative():
    for p in (_EMPTY, _MINIMAL, _SHAPES):
        assert fodg_shape_count_div_page_count(p) >= 0

def test_shape_count_div_page_count_ordering():
    assert (fodg_shape_count_div_page_count(_EMPTY) <
            fodg_shape_count_div_page_count(_MINIMAL) <
            fodg_shape_count_div_page_count(_SHAPES))


# fodg_has_more_shapes_than_text — empty=False, minimal=False, shapes-basic=True
def test_has_more_shapes_than_text_empty():
    assert fodg_has_more_shapes_than_text(_EMPTY) is False

def test_has_more_shapes_than_text_minimal():
    assert fodg_has_more_shapes_than_text(_MINIMAL) is False

def test_has_more_shapes_than_text_shapes():
    assert fodg_has_more_shapes_than_text(_SHAPES) is True

def test_has_more_shapes_than_text_type_empty():
    assert isinstance(fodg_has_more_shapes_than_text(_EMPTY), bool)

def test_has_more_shapes_than_text_type_shapes():
    assert isinstance(fodg_has_more_shapes_than_text(_SHAPES), bool)

def test_has_more_shapes_than_text_false_for_empty():
    result = fodg_has_more_shapes_than_text(_EMPTY)
    assert result is False
