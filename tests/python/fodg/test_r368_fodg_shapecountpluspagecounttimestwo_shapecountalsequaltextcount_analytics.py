"""
Sprint r368: FODG analytics tests.
fodg_shape_count_plus_page_count_times_two + fodg_shape_count_equals_text_count
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import (
    fodg_shape_count_plus_page_count_times_two,
    fodg_shape_count_equals_text_count,
)

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_shape_count_plus_page_count_times_two
def test_shape_plus_page_times_two_empty():
    assert fodg_shape_count_plus_page_count_times_two(_EMPTY) == 2

def test_shape_plus_page_times_two_minimal():
    assert fodg_shape_count_plus_page_count_times_two(_MINIMAL) == 3

def test_shape_plus_page_times_two_shapes():
    assert fodg_shape_count_plus_page_count_times_two(_SHAPES) == 5

def test_shape_plus_page_times_two_empty_type():
    assert isinstance(fodg_shape_count_plus_page_count_times_two(_EMPTY), int)

def test_shape_plus_page_times_two_minimal_type():
    assert isinstance(fodg_shape_count_plus_page_count_times_two(_MINIMAL), int)

def test_shape_plus_page_times_two_shapes_type():
    assert isinstance(fodg_shape_count_plus_page_count_times_two(_SHAPES), int)

def test_shape_plus_page_times_two_empty_positive():
    assert fodg_shape_count_plus_page_count_times_two(_EMPTY) > 0

def test_shape_plus_page_times_two_empty_not_minimal():
    assert fodg_shape_count_plus_page_count_times_two(_EMPTY) != fodg_shape_count_plus_page_count_times_two(_MINIMAL)

def test_shape_plus_page_times_two_empty_not_shapes():
    assert fodg_shape_count_plus_page_count_times_two(_EMPTY) != fodg_shape_count_plus_page_count_times_two(_SHAPES)

def test_shape_plus_page_times_two_minimal_not_shapes():
    assert fodg_shape_count_plus_page_count_times_two(_MINIMAL) != fodg_shape_count_plus_page_count_times_two(_SHAPES)

def test_shape_plus_page_times_two_shapes_greatest():
    v_e = fodg_shape_count_plus_page_count_times_two(_EMPTY)
    v_m = fodg_shape_count_plus_page_count_times_two(_MINIMAL)
    v_s = fodg_shape_count_plus_page_count_times_two(_SHAPES)
    assert v_s > v_m > v_e

def test_shape_plus_page_times_two_empty_two():
    assert fodg_shape_count_plus_page_count_times_two(_EMPTY) == 2


# fodg_shape_count_equals_text_count
def test_shape_eq_text_empty():
    assert fodg_shape_count_equals_text_count(_EMPTY) is True

def test_shape_eq_text_minimal():
    assert fodg_shape_count_equals_text_count(_MINIMAL) is True

def test_shape_eq_text_shapes():
    assert fodg_shape_count_equals_text_count(_SHAPES) is False

def test_shape_eq_text_empty_type():
    assert isinstance(fodg_shape_count_equals_text_count(_EMPTY), bool)

def test_shape_eq_text_minimal_type():
    assert isinstance(fodg_shape_count_equals_text_count(_MINIMAL), bool)

def test_shape_eq_text_shapes_type():
    assert isinstance(fodg_shape_count_equals_text_count(_SHAPES), bool)

def test_shape_eq_text_empty_true():
    assert fodg_shape_count_equals_text_count(_EMPTY)

def test_shape_eq_text_minimal_true():
    assert fodg_shape_count_equals_text_count(_MINIMAL)

def test_shape_eq_text_shapes_false():
    assert not fodg_shape_count_equals_text_count(_SHAPES)

def test_shape_eq_text_empty_minimal_same():
    assert fodg_shape_count_equals_text_count(_EMPTY) == fodg_shape_count_equals_text_count(_MINIMAL)

def test_shape_eq_text_shapes_differs_empty():
    assert fodg_shape_count_equals_text_count(_SHAPES) != fodg_shape_count_equals_text_count(_EMPTY)

def test_shape_eq_text_shapes_differs_minimal():
    assert fodg_shape_count_equals_text_count(_SHAPES) != fodg_shape_count_equals_text_count(_MINIMAL)
