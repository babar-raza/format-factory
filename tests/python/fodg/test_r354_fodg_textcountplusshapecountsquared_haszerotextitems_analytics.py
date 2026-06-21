"""
Sprint r354: fodg_text_count_plus_shape_count_squared + fodg_has_zero_text_items tests.
empty-page.fodg:       text=0, shapes=0 → 0+0=0;   zero_text=True
minimal-drawing.fodg:  text=1, shapes=1 → 1+1=2;   zero_text=False
shapes-basic.fodg:     text=2, shapes=3 → 2+9=11;  zero_text=False
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import fodg_text_count_plus_shape_count_squared, fodg_has_zero_text_items

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_text_count_plus_shape_count_squared
def test_text_plus_shape_sq_empty():
    assert fodg_text_count_plus_shape_count_squared(_EMPTY) == 0

def test_text_plus_shape_sq_minimal():
    assert fodg_text_count_plus_shape_count_squared(_MINIMAL) == 2

def test_text_plus_shape_sq_shapes():
    assert fodg_text_count_plus_shape_count_squared(_SHAPES) == 11

def test_text_plus_shape_sq_returns_int():
    assert isinstance(fodg_text_count_plus_shape_count_squared(_EMPTY), int)

def test_text_plus_shape_sq_nonnegative():
    assert fodg_text_count_plus_shape_count_squared(_EMPTY) >= 0

def test_text_plus_shape_sq_distinct_values():
    vals = {
        fodg_text_count_plus_shape_count_squared(_EMPTY),
        fodg_text_count_plus_shape_count_squared(_MINIMAL),
        fodg_text_count_plus_shape_count_squared(_SHAPES),
    }
    assert len(vals) == 3


# fodg_has_zero_text_items
def test_has_zero_text_items_empty_true():
    assert fodg_has_zero_text_items(_EMPTY) is True

def test_has_zero_text_items_minimal_false():
    assert fodg_has_zero_text_items(_MINIMAL) is False

def test_has_zero_text_items_shapes_false():
    assert fodg_has_zero_text_items(_SHAPES) is False

def test_has_zero_text_items_returns_bool():
    assert isinstance(fodg_has_zero_text_items(_EMPTY), bool)

def test_has_zero_text_items_both_branches():
    assert fodg_has_zero_text_items(_EMPTY) is True
    assert fodg_has_zero_text_items(_SHAPES) is False

def test_has_zero_text_items_minimal_no():
    assert not fodg_has_zero_text_items(_MINIMAL)
