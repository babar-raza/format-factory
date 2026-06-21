"""
Sprint r370: FODG analytics tests.
fodg_shape_count_cubed + fodg_shape_count_is_odd
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import (
    fodg_shape_count_cubed,
    fodg_shape_count_is_odd,
)

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_shape_count_cubed
def test_shape_cubed_empty():
    assert fodg_shape_count_cubed(_EMPTY) == 0

def test_shape_cubed_minimal():
    assert fodg_shape_count_cubed(_MINIMAL) == 1

def test_shape_cubed_shapes():
    assert fodg_shape_count_cubed(_SHAPES) == 27

def test_shape_cubed_empty_type():
    assert isinstance(fodg_shape_count_cubed(_EMPTY), int)

def test_shape_cubed_minimal_type():
    assert isinstance(fodg_shape_count_cubed(_MINIMAL), int)

def test_shape_cubed_shapes_type():
    assert isinstance(fodg_shape_count_cubed(_SHAPES), int)

def test_shape_cubed_empty_nonneg():
    assert fodg_shape_count_cubed(_EMPTY) >= 0

def test_shape_cubed_empty_not_minimal():
    assert fodg_shape_count_cubed(_EMPTY) != fodg_shape_count_cubed(_MINIMAL)

def test_shape_cubed_empty_not_shapes():
    assert fodg_shape_count_cubed(_EMPTY) != fodg_shape_count_cubed(_SHAPES)

def test_shape_cubed_minimal_not_shapes():
    assert fodg_shape_count_cubed(_MINIMAL) != fodg_shape_count_cubed(_SHAPES)

def test_shape_cubed_shapes_greatest():
    v_e = fodg_shape_count_cubed(_EMPTY)
    v_m = fodg_shape_count_cubed(_MINIMAL)
    v_s = fodg_shape_count_cubed(_SHAPES)
    assert v_s > v_m > v_e

def test_shape_cubed_empty_zero():
    assert fodg_shape_count_cubed(_EMPTY) == 0


# fodg_shape_count_is_odd
def test_shape_is_odd_empty():
    assert fodg_shape_count_is_odd(_EMPTY) is False

def test_shape_is_odd_minimal():
    assert fodg_shape_count_is_odd(_MINIMAL) is True

def test_shape_is_odd_shapes():
    assert fodg_shape_count_is_odd(_SHAPES) is True

def test_shape_is_odd_empty_type():
    assert isinstance(fodg_shape_count_is_odd(_EMPTY), bool)

def test_shape_is_odd_minimal_type():
    assert isinstance(fodg_shape_count_is_odd(_MINIMAL), bool)

def test_shape_is_odd_shapes_type():
    assert isinstance(fodg_shape_count_is_odd(_SHAPES), bool)

def test_shape_is_odd_empty_false():
    assert not fodg_shape_count_is_odd(_EMPTY)

def test_shape_is_odd_minimal_true():
    assert fodg_shape_count_is_odd(_MINIMAL)

def test_shape_is_odd_shapes_true():
    assert fodg_shape_count_is_odd(_SHAPES)

def test_shape_is_odd_minimal_shapes_same():
    assert fodg_shape_count_is_odd(_MINIMAL) == fodg_shape_count_is_odd(_SHAPES)

def test_shape_is_odd_empty_differs_minimal():
    assert fodg_shape_count_is_odd(_EMPTY) != fodg_shape_count_is_odd(_MINIMAL)

def test_shape_is_odd_empty_differs_shapes():
    assert fodg_shape_count_is_odd(_EMPTY) != fodg_shape_count_is_odd(_SHAPES)
