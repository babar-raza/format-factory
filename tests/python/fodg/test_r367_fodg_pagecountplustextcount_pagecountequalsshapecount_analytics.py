"""
Sprint r367: FODG analytics tests.
fodg_page_count_plus_text_count + fodg_page_count_equals_shape_count
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import (
    fodg_page_count_plus_text_count,
    fodg_page_count_equals_shape_count,
)

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_page_count_plus_text_count
def test_page_plus_text_empty():
    assert fodg_page_count_plus_text_count(_EMPTY) == 1

def test_page_plus_text_minimal():
    assert fodg_page_count_plus_text_count(_MINIMAL) == 2

def test_page_plus_text_shapes():
    assert fodg_page_count_plus_text_count(_SHAPES) == 3

def test_page_plus_text_empty_type():
    assert isinstance(fodg_page_count_plus_text_count(_EMPTY), int)

def test_page_plus_text_minimal_type():
    assert isinstance(fodg_page_count_plus_text_count(_MINIMAL), int)

def test_page_plus_text_shapes_type():
    assert isinstance(fodg_page_count_plus_text_count(_SHAPES), int)

def test_page_plus_text_empty_positive():
    assert fodg_page_count_plus_text_count(_EMPTY) > 0

def test_page_plus_text_empty_not_minimal():
    assert fodg_page_count_plus_text_count(_EMPTY) != fodg_page_count_plus_text_count(_MINIMAL)

def test_page_plus_text_empty_not_shapes():
    assert fodg_page_count_plus_text_count(_EMPTY) != fodg_page_count_plus_text_count(_SHAPES)

def test_page_plus_text_minimal_not_shapes():
    assert fodg_page_count_plus_text_count(_MINIMAL) != fodg_page_count_plus_text_count(_SHAPES)

def test_page_plus_text_shapes_greatest():
    v_e = fodg_page_count_plus_text_count(_EMPTY)
    v_m = fodg_page_count_plus_text_count(_MINIMAL)
    v_s = fodg_page_count_plus_text_count(_SHAPES)
    assert v_s > v_m > v_e

def test_page_plus_text_empty_one():
    assert fodg_page_count_plus_text_count(_EMPTY) == 1


# fodg_page_count_equals_shape_count
def test_page_eq_shape_empty():
    assert fodg_page_count_equals_shape_count(_EMPTY) is False

def test_page_eq_shape_minimal():
    assert fodg_page_count_equals_shape_count(_MINIMAL) is True

def test_page_eq_shape_shapes():
    assert fodg_page_count_equals_shape_count(_SHAPES) is False

def test_page_eq_shape_empty_type():
    assert isinstance(fodg_page_count_equals_shape_count(_EMPTY), bool)

def test_page_eq_shape_minimal_type():
    assert isinstance(fodg_page_count_equals_shape_count(_MINIMAL), bool)

def test_page_eq_shape_shapes_type():
    assert isinstance(fodg_page_count_equals_shape_count(_SHAPES), bool)

def test_page_eq_shape_empty_false():
    assert not fodg_page_count_equals_shape_count(_EMPTY)

def test_page_eq_shape_minimal_true():
    assert fodg_page_count_equals_shape_count(_MINIMAL)

def test_page_eq_shape_shapes_false():
    assert not fodg_page_count_equals_shape_count(_SHAPES)

def test_page_eq_shape_empty_shapes_same():
    assert fodg_page_count_equals_shape_count(_EMPTY) == fodg_page_count_equals_shape_count(_SHAPES)

def test_page_eq_shape_minimal_differs_empty():
    assert fodg_page_count_equals_shape_count(_MINIMAL) != fodg_page_count_equals_shape_count(_EMPTY)

def test_page_eq_shape_minimal_differs_shapes():
    assert fodg_page_count_equals_shape_count(_MINIMAL) != fodg_page_count_equals_shape_count(_SHAPES)
