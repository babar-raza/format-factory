"""
Sprint r356: fodg_page_count_plus_text_times_two + fodg_shape_count_is_even tests.
empty-page.fodg:      text=0, shapes=0, pages=1 → 1+0*2=1;  0%2==0=True
minimal-drawing.fodg: text=1, shapes=1, pages=1 → 1+1*2=3;  1%2==0=False
shapes-basic.fodg:    text=2, shapes=3, pages=1 → 1+2*2=5;  3%2==0=False
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import (
    fodg_page_count_plus_text_times_two,
    fodg_shape_count_is_even,
)

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_page_count_plus_text_times_two
def test_page_plus_text_times_two_empty():
    assert fodg_page_count_plus_text_times_two(_EMPTY) == 1

def test_page_plus_text_times_two_minimal():
    assert fodg_page_count_plus_text_times_two(_MINIMAL) == 3

def test_page_plus_text_times_two_shapes():
    assert fodg_page_count_plus_text_times_two(_SHAPES) == 5

def test_page_plus_text_times_two_returns_int():
    assert isinstance(fodg_page_count_plus_text_times_two(_EMPTY), int)

def test_page_plus_text_times_two_positive():
    assert fodg_page_count_plus_text_times_two(_EMPTY) > 0

def test_page_plus_text_times_two_distinct():
    vals = {
        fodg_page_count_plus_text_times_two(_EMPTY),
        fodg_page_count_plus_text_times_two(_MINIMAL),
        fodg_page_count_plus_text_times_two(_SHAPES),
    }
    assert len(vals) == 3


# fodg_shape_count_is_even
def test_shape_count_is_even_empty_true():
    assert fodg_shape_count_is_even(_EMPTY) is True

def test_shape_count_is_even_minimal_false():
    assert fodg_shape_count_is_even(_MINIMAL) is False

def test_shape_count_is_even_shapes_false():
    assert fodg_shape_count_is_even(_SHAPES) is False

def test_shape_count_is_even_returns_bool():
    assert isinstance(fodg_shape_count_is_even(_EMPTY), bool)

def test_shape_count_is_even_both_branches():
    assert fodg_shape_count_is_even(_EMPTY) is True
    assert fodg_shape_count_is_even(_SHAPES) is False

def test_shape_count_is_even_minimal_no():
    assert not fodg_shape_count_is_even(_MINIMAL)
