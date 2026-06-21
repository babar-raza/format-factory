"""
Sprint r352: fodg_text_count_times_shape_count + fodg_is_single_shape_drawing tests.
empty-page.fodg:       text=0, shapes=0 → product=0;  single_shape=False
minimal-drawing.fodg:  text=1, shapes=1 → product=1;  single_shape=True
shapes-basic.fodg:     text=2, shapes=3 → product=6;  single_shape=False
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import fodg_text_count_times_shape_count, fodg_is_single_shape_drawing

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_text_count_times_shape_count
def test_text_times_shape_empty():
    assert fodg_text_count_times_shape_count(_EMPTY) == 0

def test_text_times_shape_minimal():
    assert fodg_text_count_times_shape_count(_MINIMAL) == 1

def test_text_times_shape_shapes():
    assert fodg_text_count_times_shape_count(_SHAPES) == 6

def test_text_times_shape_returns_int():
    assert isinstance(fodg_text_count_times_shape_count(_EMPTY), int)

def test_text_times_shape_nonnegative():
    assert fodg_text_count_times_shape_count(_EMPTY) >= 0

def test_text_times_shape_distinct_values():
    vals = {
        fodg_text_count_times_shape_count(_EMPTY),
        fodg_text_count_times_shape_count(_MINIMAL),
        fodg_text_count_times_shape_count(_SHAPES),
    }
    assert len(vals) == 3


# fodg_is_single_shape_drawing
def test_is_single_shape_drawing_empty_false():
    assert fodg_is_single_shape_drawing(_EMPTY) is False

def test_is_single_shape_drawing_minimal_true():
    assert fodg_is_single_shape_drawing(_MINIMAL) is True

def test_is_single_shape_drawing_shapes_false():
    assert fodg_is_single_shape_drawing(_SHAPES) is False

def test_is_single_shape_drawing_returns_bool():
    assert isinstance(fodg_is_single_shape_drawing(_EMPTY), bool)

def test_is_single_shape_drawing_both_branches():
    assert fodg_is_single_shape_drawing(_MINIMAL) is True
    assert fodg_is_single_shape_drawing(_SHAPES) is False

def test_is_single_shape_drawing_empty_no():
    assert not fodg_is_single_shape_drawing(_EMPTY)
