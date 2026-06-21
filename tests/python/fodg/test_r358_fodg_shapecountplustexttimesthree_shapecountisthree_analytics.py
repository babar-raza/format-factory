"""
Sprint r358: fodg_shape_count_plus_text_times_three + fodg_shape_count_is_three tests.
empty-page.fodg:      shapes=0, text=0 → 0+0*3=0;   shapes==3=False
minimal-drawing.fodg: shapes=1, text=1 → 1+1*3=4;   shapes==3=False
shapes-basic.fodg:    shapes=3, text=2 → 3+2*3=9;   shapes==3=True
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import (
    fodg_shape_count_plus_text_times_three,
    fodg_shape_count_is_three,
)

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_shape_count_plus_text_times_three
def test_shape_plus_text_times_three_empty():
    assert fodg_shape_count_plus_text_times_three(_EMPTY) == 0

def test_shape_plus_text_times_three_minimal():
    assert fodg_shape_count_plus_text_times_three(_MINIMAL) == 4

def test_shape_plus_text_times_three_shapes():
    assert fodg_shape_count_plus_text_times_three(_SHAPES) == 9

def test_shape_plus_text_times_three_returns_int():
    assert isinstance(fodg_shape_count_plus_text_times_three(_EMPTY), int)

def test_shape_plus_text_times_three_nonnegative():
    assert fodg_shape_count_plus_text_times_three(_EMPTY) >= 0

def test_shape_plus_text_times_three_distinct():
    vals = {
        fodg_shape_count_plus_text_times_three(_EMPTY),
        fodg_shape_count_plus_text_times_three(_MINIMAL),
        fodg_shape_count_plus_text_times_three(_SHAPES),
    }
    assert len(vals) == 3


# fodg_shape_count_is_three
def test_shape_count_is_three_empty_false():
    assert fodg_shape_count_is_three(_EMPTY) is False

def test_shape_count_is_three_minimal_false():
    assert fodg_shape_count_is_three(_MINIMAL) is False

def test_shape_count_is_three_shapes_true():
    assert fodg_shape_count_is_three(_SHAPES) is True

def test_shape_count_is_three_returns_bool():
    assert isinstance(fodg_shape_count_is_three(_SHAPES), bool)

def test_shape_count_is_three_both_branches():
    assert fodg_shape_count_is_three(_SHAPES) is True
    assert fodg_shape_count_is_three(_EMPTY) is False

def test_shape_count_is_three_minimal_no():
    assert not fodg_shape_count_is_three(_MINIMAL)
