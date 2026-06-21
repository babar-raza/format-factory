"""
Sprint r369: FODG analytics tests.
fodg_text_count_squared + fodg_text_count_not_equal_shape_count
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import (
    fodg_text_count_squared,
    fodg_text_count_not_equal_shape_count,
)

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_text_count_squared
def test_text_squared_empty():
    assert fodg_text_count_squared(_EMPTY) == 0

def test_text_squared_minimal():
    assert fodg_text_count_squared(_MINIMAL) == 1

def test_text_squared_shapes():
    assert fodg_text_count_squared(_SHAPES) == 4

def test_text_squared_empty_type():
    assert isinstance(fodg_text_count_squared(_EMPTY), int)

def test_text_squared_minimal_type():
    assert isinstance(fodg_text_count_squared(_MINIMAL), int)

def test_text_squared_shapes_type():
    assert isinstance(fodg_text_count_squared(_SHAPES), int)

def test_text_squared_empty_nonneg():
    assert fodg_text_count_squared(_EMPTY) >= 0

def test_text_squared_empty_not_minimal():
    assert fodg_text_count_squared(_EMPTY) != fodg_text_count_squared(_MINIMAL)

def test_text_squared_empty_not_shapes():
    assert fodg_text_count_squared(_EMPTY) != fodg_text_count_squared(_SHAPES)

def test_text_squared_minimal_not_shapes():
    assert fodg_text_count_squared(_MINIMAL) != fodg_text_count_squared(_SHAPES)

def test_text_squared_shapes_greatest():
    v_e = fodg_text_count_squared(_EMPTY)
    v_m = fodg_text_count_squared(_MINIMAL)
    v_s = fodg_text_count_squared(_SHAPES)
    assert v_s > v_m > v_e

def test_text_squared_empty_zero():
    assert fodg_text_count_squared(_EMPTY) == 0


# fodg_text_count_not_equal_shape_count
def test_text_not_eq_shape_empty():
    assert fodg_text_count_not_equal_shape_count(_EMPTY) is False

def test_text_not_eq_shape_minimal():
    assert fodg_text_count_not_equal_shape_count(_MINIMAL) is False

def test_text_not_eq_shape_shapes():
    assert fodg_text_count_not_equal_shape_count(_SHAPES) is True

def test_text_not_eq_shape_empty_type():
    assert isinstance(fodg_text_count_not_equal_shape_count(_EMPTY), bool)

def test_text_not_eq_shape_minimal_type():
    assert isinstance(fodg_text_count_not_equal_shape_count(_MINIMAL), bool)

def test_text_not_eq_shape_shapes_type():
    assert isinstance(fodg_text_count_not_equal_shape_count(_SHAPES), bool)

def test_text_not_eq_shape_empty_false():
    assert not fodg_text_count_not_equal_shape_count(_EMPTY)

def test_text_not_eq_shape_minimal_false():
    assert not fodg_text_count_not_equal_shape_count(_MINIMAL)

def test_text_not_eq_shape_shapes_true():
    assert fodg_text_count_not_equal_shape_count(_SHAPES)

def test_text_not_eq_shape_empty_minimal_same():
    assert fodg_text_count_not_equal_shape_count(_EMPTY) == fodg_text_count_not_equal_shape_count(_MINIMAL)

def test_text_not_eq_shape_shapes_differs_empty():
    assert fodg_text_count_not_equal_shape_count(_SHAPES) != fodg_text_count_not_equal_shape_count(_EMPTY)

def test_text_not_eq_shape_shapes_differs_minimal():
    assert fodg_text_count_not_equal_shape_count(_SHAPES) != fodg_text_count_not_equal_shape_count(_MINIMAL)
