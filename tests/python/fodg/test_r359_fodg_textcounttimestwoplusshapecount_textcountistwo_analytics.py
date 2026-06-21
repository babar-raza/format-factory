"""
Sprint r359: fodg_text_count_times_two_plus_shape_count + fodg_text_count_is_two tests.
empty-page.fodg:      text=0, shapes=0 → 0*2+0=0;  text==2=False
minimal-drawing.fodg: text=1, shapes=1 → 1*2+1=3;  text==2=False
shapes-basic.fodg:    text=2, shapes=3 → 2*2+3=7;  text==2=True
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import (
    fodg_text_count_times_two_plus_shape_count,
    fodg_text_count_is_two,
)

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_text_count_times_two_plus_shape_count
def test_text_times_two_plus_shape_empty():
    assert fodg_text_count_times_two_plus_shape_count(_EMPTY) == 0

def test_text_times_two_plus_shape_minimal():
    assert fodg_text_count_times_two_plus_shape_count(_MINIMAL) == 3

def test_text_times_two_plus_shape_shapes():
    assert fodg_text_count_times_two_plus_shape_count(_SHAPES) == 7

def test_text_times_two_plus_shape_returns_int():
    assert isinstance(fodg_text_count_times_two_plus_shape_count(_EMPTY), int)

def test_text_times_two_plus_shape_nonnegative():
    assert fodg_text_count_times_two_plus_shape_count(_EMPTY) >= 0

def test_text_times_two_plus_shape_distinct():
    vals = {
        fodg_text_count_times_two_plus_shape_count(_EMPTY),
        fodg_text_count_times_two_plus_shape_count(_MINIMAL),
        fodg_text_count_times_two_plus_shape_count(_SHAPES),
    }
    assert len(vals) == 3


# fodg_text_count_is_two
def test_text_count_is_two_empty_false():
    assert fodg_text_count_is_two(_EMPTY) is False

def test_text_count_is_two_minimal_false():
    assert fodg_text_count_is_two(_MINIMAL) is False

def test_text_count_is_two_shapes_true():
    assert fodg_text_count_is_two(_SHAPES) is True

def test_text_count_is_two_returns_bool():
    assert isinstance(fodg_text_count_is_two(_SHAPES), bool)

def test_text_count_is_two_both_branches():
    assert fodg_text_count_is_two(_SHAPES) is True
    assert fodg_text_count_is_two(_EMPTY) is False

def test_text_count_is_two_minimal_no():
    assert not fodg_text_count_is_two(_MINIMAL)
