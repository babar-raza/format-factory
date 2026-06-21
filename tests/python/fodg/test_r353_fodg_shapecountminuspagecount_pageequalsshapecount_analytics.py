"""
Sprint r353: fodg_shape_count_minus_page_count + fodg_page_equals_shape_count tests.
empty-page.fodg:       shapes=0, pages=1 → 0-1=-1;  pages==shapes → False(1≠0)
minimal-drawing.fodg:  shapes=1, pages=1 → 1-1=0;   pages==shapes → True(1==1)
shapes-basic.fodg:     shapes=3, pages=1 → 3-1=2;   pages==shapes → False(1≠3)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import fodg_shape_count_minus_page_count, fodg_page_equals_shape_count

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_shape_count_minus_page_count
def test_shape_minus_page_empty():
    assert fodg_shape_count_minus_page_count(_EMPTY) == -1

def test_shape_minus_page_minimal():
    assert fodg_shape_count_minus_page_count(_MINIMAL) == 0

def test_shape_minus_page_shapes():
    assert fodg_shape_count_minus_page_count(_SHAPES) == 2

def test_shape_minus_page_returns_int():
    assert isinstance(fodg_shape_count_minus_page_count(_EMPTY), int)

def test_shape_minus_page_empty_negative():
    assert fodg_shape_count_minus_page_count(_EMPTY) < 0

def test_shape_minus_page_distinct_values():
    vals = {
        fodg_shape_count_minus_page_count(_EMPTY),
        fodg_shape_count_minus_page_count(_MINIMAL),
        fodg_shape_count_minus_page_count(_SHAPES),
    }
    assert len(vals) == 3


# fodg_page_equals_shape_count
def test_page_equals_shape_empty_false():
    assert fodg_page_equals_shape_count(_EMPTY) is False

def test_page_equals_shape_minimal_true():
    assert fodg_page_equals_shape_count(_MINIMAL) is True

def test_page_equals_shape_shapes_false():
    assert fodg_page_equals_shape_count(_SHAPES) is False

def test_page_equals_shape_returns_bool():
    assert isinstance(fodg_page_equals_shape_count(_EMPTY), bool)

def test_page_equals_shape_both_branches():
    assert fodg_page_equals_shape_count(_MINIMAL) is True
    assert fodg_page_equals_shape_count(_SHAPES) is False

def test_page_equals_shape_empty_is_false():
    assert not fodg_page_equals_shape_count(_EMPTY)
