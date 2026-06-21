"""
Sprint r351: fodg_total_shape_count_plus_page_count + fodg_has_at_least_three_shapes tests.
empty-page.fodg:       shapes=0, pages=1 → sum=1;  shapes>=3 → False
minimal-drawing.fodg:  shapes=1, pages=1 → sum=2;  shapes>=3 → False
shapes-basic.fodg:     shapes=3, pages=1 → sum=4;  shapes>=3 → True
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import (
    fodg_total_shape_count_plus_page_count,
    fodg_has_at_least_three_shapes,
)

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_total_shape_count_plus_page_count
def test_shape_plus_page_empty():
    assert fodg_total_shape_count_plus_page_count(_EMPTY) == 1

def test_shape_plus_page_minimal():
    assert fodg_total_shape_count_plus_page_count(_MINIMAL) == 2

def test_shape_plus_page_shapes():
    assert fodg_total_shape_count_plus_page_count(_SHAPES) == 4

def test_shape_plus_page_returns_int():
    assert isinstance(fodg_total_shape_count_plus_page_count(_EMPTY), int)

def test_shape_plus_page_positive():
    assert fodg_total_shape_count_plus_page_count(_EMPTY) > 0

def test_shape_plus_page_distinct_values():
    vals = {
        fodg_total_shape_count_plus_page_count(_EMPTY),
        fodg_total_shape_count_plus_page_count(_MINIMAL),
        fodg_total_shape_count_plus_page_count(_SHAPES),
    }
    assert len(vals) == 3


# fodg_has_at_least_three_shapes
def test_has_at_least_three_shapes_empty_false():
    assert fodg_has_at_least_three_shapes(_EMPTY) is False

def test_has_at_least_three_shapes_minimal_false():
    assert fodg_has_at_least_three_shapes(_MINIMAL) is False

def test_has_at_least_three_shapes_shapes_true():
    assert fodg_has_at_least_three_shapes(_SHAPES) is True

def test_has_at_least_three_shapes_returns_bool():
    assert isinstance(fodg_has_at_least_three_shapes(_EMPTY), bool)

def test_has_at_least_three_shapes_both_branches():
    assert fodg_has_at_least_three_shapes(_SHAPES) is True
    assert fodg_has_at_least_three_shapes(_EMPTY) is False

def test_has_at_least_three_shapes_minimal_no():
    assert not fodg_has_at_least_three_shapes(_MINIMAL)
