"""
Sprint r371: FODG analytics tests.
fodg_text_count_cubed + fodg_text_count_is_even
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import (
    fodg_text_count_cubed,
    fodg_text_count_is_even,
)

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_text_count_cubed
# empty: 0^3=0, minimal: 1^3=1, shapes: 2^3=8
def test_text_cubed_empty():
    assert fodg_text_count_cubed(_EMPTY) == 0

def test_text_cubed_minimal():
    assert fodg_text_count_cubed(_MINIMAL) == 1

def test_text_cubed_shapes():
    assert fodg_text_count_cubed(_SHAPES) == 8

def test_text_cubed_empty_type():
    assert isinstance(fodg_text_count_cubed(_EMPTY), int)

def test_text_cubed_minimal_type():
    assert isinstance(fodg_text_count_cubed(_MINIMAL), int)

def test_text_cubed_shapes_type():
    assert isinstance(fodg_text_count_cubed(_SHAPES), int)

def test_text_cubed_empty_nonneg():
    assert fodg_text_count_cubed(_EMPTY) >= 0

def test_text_cubed_empty_not_minimal():
    assert fodg_text_count_cubed(_EMPTY) != fodg_text_count_cubed(_MINIMAL)

def test_text_cubed_empty_not_shapes():
    assert fodg_text_count_cubed(_EMPTY) != fodg_text_count_cubed(_SHAPES)

def test_text_cubed_minimal_not_shapes():
    assert fodg_text_count_cubed(_MINIMAL) != fodg_text_count_cubed(_SHAPES)

def test_text_cubed_shapes_greatest():
    v_e = fodg_text_count_cubed(_EMPTY)
    v_m = fodg_text_count_cubed(_MINIMAL)
    v_s = fodg_text_count_cubed(_SHAPES)
    assert v_s > v_m > v_e

def test_text_cubed_empty_zero():
    assert fodg_text_count_cubed(_EMPTY) == 0


# fodg_text_count_is_even
# empty: 0 % 2 == 0 → True, minimal: 1 % 2 != 0 → False, shapes: 2 % 2 == 0 → True
def test_text_even_empty():
    assert fodg_text_count_is_even(_EMPTY) is True

def test_text_even_minimal():
    assert fodg_text_count_is_even(_MINIMAL) is False

def test_text_even_shapes():
    assert fodg_text_count_is_even(_SHAPES) is True

def test_text_even_empty_type():
    assert isinstance(fodg_text_count_is_even(_EMPTY), bool)

def test_text_even_minimal_type():
    assert isinstance(fodg_text_count_is_even(_MINIMAL), bool)

def test_text_even_shapes_type():
    assert isinstance(fodg_text_count_is_even(_SHAPES), bool)

def test_text_even_empty_true():
    assert fodg_text_count_is_even(_EMPTY)

def test_text_even_minimal_false():
    assert not fodg_text_count_is_even(_MINIMAL)

def test_text_even_shapes_true():
    assert fodg_text_count_is_even(_SHAPES)

def test_text_even_empty_shapes_same():
    assert fodg_text_count_is_even(_EMPTY) == fodg_text_count_is_even(_SHAPES)

def test_text_even_minimal_differs_empty():
    assert fodg_text_count_is_even(_MINIMAL) != fodg_text_count_is_even(_EMPTY)

def test_text_even_minimal_differs_shapes():
    assert fodg_text_count_is_even(_MINIMAL) != fodg_text_count_is_even(_SHAPES)
