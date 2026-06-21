"""
Sprint r345: fodg_max_shapes_plus_text_count + fodg_has_equal_shapes_and_text.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_max_shapes_plus_text_count,
    fodg_has_equal_shapes_and_text,
)

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES = _FODG / "shapes-basic.fodg"


# fodg_max_shapes_plus_text_count — empty=0, minimal=2, shapes-basic=5
def test_max_shapes_plus_text_count_empty():
    assert fodg_max_shapes_plus_text_count(_EMPTY) == 0

def test_max_shapes_plus_text_count_minimal():
    assert fodg_max_shapes_plus_text_count(_MINIMAL) == 2

def test_max_shapes_plus_text_count_shapes():
    assert fodg_max_shapes_plus_text_count(_SHAPES) == 5

def test_max_shapes_plus_text_count_type():
    assert isinstance(fodg_max_shapes_plus_text_count(_EMPTY), int)

def test_max_shapes_plus_text_count_nonnegative():
    for p in (_EMPTY, _MINIMAL, _SHAPES):
        assert fodg_max_shapes_plus_text_count(p) >= 0

def test_max_shapes_plus_text_count_ordering():
    assert (fodg_max_shapes_plus_text_count(_EMPTY) <
            fodg_max_shapes_plus_text_count(_MINIMAL) <
            fodg_max_shapes_plus_text_count(_SHAPES))


# fodg_has_equal_shapes_and_text — empty=True, minimal=True, shapes-basic=False
def test_has_equal_shapes_and_text_empty():
    assert fodg_has_equal_shapes_and_text(_EMPTY) is True

def test_has_equal_shapes_and_text_minimal():
    assert fodg_has_equal_shapes_and_text(_MINIMAL) is True

def test_has_equal_shapes_and_text_shapes():
    assert fodg_has_equal_shapes_and_text(_SHAPES) is False

def test_has_equal_shapes_and_text_type_empty():
    assert isinstance(fodg_has_equal_shapes_and_text(_EMPTY), bool)

def test_has_equal_shapes_and_text_type_shapes():
    assert isinstance(fodg_has_equal_shapes_and_text(_SHAPES), bool)

def test_has_equal_shapes_and_text_false_for_shapes():
    result = fodg_has_equal_shapes_and_text(_SHAPES)
    assert result is False
