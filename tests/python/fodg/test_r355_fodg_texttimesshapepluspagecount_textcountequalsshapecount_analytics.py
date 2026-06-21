"""
Sprint r355: fodg_text_times_shape_plus_page_count + fodg_text_count_equals_shape_count tests.
empty-page.fodg:      text=0, shapes=0, pages=1 → 0*0+1=1;  text==shapes=True
minimal-drawing.fodg: text=1, shapes=1, pages=1 → 1*1+1=2;  text==shapes=True
shapes-basic.fodg:    text=2, shapes=3, pages=1 → 2*3+1=7;  text==shapes=False
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import (
    fodg_text_times_shape_plus_page_count,
    fodg_text_count_equals_shape_count,
)

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_text_times_shape_plus_page_count
def test_text_times_shape_plus_page_empty():
    assert fodg_text_times_shape_plus_page_count(_EMPTY) == 1

def test_text_times_shape_plus_page_minimal():
    assert fodg_text_times_shape_plus_page_count(_MINIMAL) == 2

def test_text_times_shape_plus_page_shapes():
    assert fodg_text_times_shape_plus_page_count(_SHAPES) == 7

def test_text_times_shape_plus_page_returns_int():
    assert isinstance(fodg_text_times_shape_plus_page_count(_EMPTY), int)

def test_text_times_shape_plus_page_positive():
    assert fodg_text_times_shape_plus_page_count(_EMPTY) > 0

def test_text_times_shape_plus_page_distinct():
    vals = {
        fodg_text_times_shape_plus_page_count(_EMPTY),
        fodg_text_times_shape_plus_page_count(_MINIMAL),
        fodg_text_times_shape_plus_page_count(_SHAPES),
    }
    assert len(vals) == 3


# fodg_text_count_equals_shape_count
def test_text_equals_shape_empty_true():
    assert fodg_text_count_equals_shape_count(_EMPTY) is True

def test_text_equals_shape_minimal_true():
    assert fodg_text_count_equals_shape_count(_MINIMAL) is True

def test_text_equals_shape_shapes_false():
    assert fodg_text_count_equals_shape_count(_SHAPES) is False

def test_text_equals_shape_returns_bool():
    assert isinstance(fodg_text_count_equals_shape_count(_EMPTY), bool)

def test_text_equals_shape_both_branches():
    assert fodg_text_count_equals_shape_count(_EMPTY) is True
    assert fodg_text_count_equals_shape_count(_SHAPES) is False

def test_text_equals_shape_shapes_no():
    assert not fodg_text_count_equals_shape_count(_SHAPES)
