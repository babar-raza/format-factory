"""Tests for fodg_shape_count_squared_plus_text_count and fodg_text_count_less_than_shape_count (r362)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import (
    fodg_shape_count_squared_plus_text_count,
    fodg_text_count_less_than_shape_count,
)

_FODG = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES = _FODG / "shapes-basic.fodg"


# fodg_shape_count_squared_plus_text_count
# empty-page:      shapes=0, text=0 => 0^2+0 = 0
# minimal-drawing: shapes=1, text=1 => 1^2+1 = 2
# shapes-basic:    shapes=3, text=2 => 3^2+2 = 11

def test_shape_squared_plus_text_empty():
    assert fodg_shape_count_squared_plus_text_count(_EMPTY) == 0


def test_shape_squared_plus_text_minimal():
    assert fodg_shape_count_squared_plus_text_count(_MINIMAL) == 2


def test_shape_squared_plus_text_shapes():
    assert fodg_shape_count_squared_plus_text_count(_SHAPES) == 11


def test_shape_squared_plus_text_empty_is_int():
    assert isinstance(fodg_shape_count_squared_plus_text_count(_EMPTY), int)


def test_shape_squared_plus_text_minimal_is_int():
    assert isinstance(fodg_shape_count_squared_plus_text_count(_MINIMAL), int)


def test_shape_squared_plus_text_distinct():
    v1 = fodg_shape_count_squared_plus_text_count(_EMPTY)
    v2 = fodg_shape_count_squared_plus_text_count(_MINIMAL)
    v3 = fodg_shape_count_squared_plus_text_count(_SHAPES)
    assert len({v1, v2, v3}) == 3


# fodg_text_count_less_than_shape_count
# empty-page:      text=0, shapes=0 => False (0 < 0 is False)
# minimal-drawing: text=1, shapes=1 => False (1 < 1 is False)
# shapes-basic:    text=2, shapes=3 => True  (2 < 3)

def test_text_less_than_shape_empty_is_false():
    assert fodg_text_count_less_than_shape_count(_EMPTY) is False


def test_text_less_than_shape_minimal_is_false():
    assert fodg_text_count_less_than_shape_count(_MINIMAL) is False


def test_text_less_than_shape_shapes_is_true():
    assert fodg_text_count_less_than_shape_count(_SHAPES) is True


def test_text_less_than_shape_empty_is_bool():
    assert isinstance(fodg_text_count_less_than_shape_count(_EMPTY), bool)


def test_text_less_than_shape_minimal_is_bool():
    assert isinstance(fodg_text_count_less_than_shape_count(_MINIMAL), bool)


def test_text_less_than_shape_both_true_and_false():
    results = [
        fodg_text_count_less_than_shape_count(_EMPTY),
        fodg_text_count_less_than_shape_count(_MINIMAL),
        fodg_text_count_less_than_shape_count(_SHAPES),
    ]
    assert True in results and False in results
