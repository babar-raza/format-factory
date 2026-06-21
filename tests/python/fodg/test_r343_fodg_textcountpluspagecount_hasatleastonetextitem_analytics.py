"""
Sprint r343: fodg_text_count_plus_page_count + fodg_has_at_least_one_text_item.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_text_count_plus_page_count,
    fodg_has_at_least_one_text_item,
)

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES = _FODG / "shapes-basic.fodg"


# fodg_text_count_plus_page_count — empty=1, minimal=2, shapes-basic=3
def test_text_count_plus_page_count_empty():
    assert fodg_text_count_plus_page_count(_EMPTY) == 1

def test_text_count_plus_page_count_minimal():
    assert fodg_text_count_plus_page_count(_MINIMAL) == 2

def test_text_count_plus_page_count_shapes():
    assert fodg_text_count_plus_page_count(_SHAPES) == 3

def test_text_count_plus_page_count_type():
    assert isinstance(fodg_text_count_plus_page_count(_EMPTY), int)

def test_text_count_plus_page_count_nonnegative():
    for p in (_EMPTY, _MINIMAL, _SHAPES):
        assert fodg_text_count_plus_page_count(p) >= 0

def test_text_count_plus_page_count_ordering():
    assert (fodg_text_count_plus_page_count(_EMPTY) <
            fodg_text_count_plus_page_count(_MINIMAL) <
            fodg_text_count_plus_page_count(_SHAPES))


# fodg_has_at_least_one_text_item — empty=False, minimal=True, shapes-basic=True
def test_has_at_least_one_text_item_empty():
    assert fodg_has_at_least_one_text_item(_EMPTY) is False

def test_has_at_least_one_text_item_minimal():
    assert fodg_has_at_least_one_text_item(_MINIMAL) is True

def test_has_at_least_one_text_item_shapes():
    assert fodg_has_at_least_one_text_item(_SHAPES) is True

def test_has_at_least_one_text_item_type_empty():
    assert isinstance(fodg_has_at_least_one_text_item(_EMPTY), bool)

def test_has_at_least_one_text_item_type_minimal():
    assert isinstance(fodg_has_at_least_one_text_item(_MINIMAL), bool)

def test_has_at_least_one_text_item_false_for_empty():
    result = fodg_has_at_least_one_text_item(_EMPTY)
    assert result is False
