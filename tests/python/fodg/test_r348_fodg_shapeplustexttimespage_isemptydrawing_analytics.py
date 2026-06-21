"""
Sprint r348: fodg_shape_plus_text_times_page + fodg_is_empty_drawing analytics tests.
empty-page.fodg:       shapes=0, text=0, pages=1 → (0+0)*1=0,  is_empty=True
minimal-drawing.fodg:  shapes=1, text=1, pages=1 → (1+1)*1=2,  is_empty=False
shapes-basic.fodg:     shapes=3, text=2, pages=1 → (3+2)*1=5,  is_empty=False
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import fodg_shape_plus_text_times_page, fodg_is_empty_drawing

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_shape_plus_text_times_page
def test_shape_plus_text_times_page_empty():
    assert fodg_shape_plus_text_times_page(_EMPTY) == 0

def test_shape_plus_text_times_page_minimal():
    assert fodg_shape_plus_text_times_page(_MINIMAL) == 2

def test_shape_plus_text_times_page_shapes():
    assert fodg_shape_plus_text_times_page(_SHAPES) == 5

def test_shape_plus_text_times_page_returns_int():
    assert isinstance(fodg_shape_plus_text_times_page(_EMPTY), int)

def test_shape_plus_text_times_page_nonnegative():
    assert fodg_shape_plus_text_times_page(_EMPTY) >= 0

def test_shape_plus_text_times_page_distinct_values():
    vals = {
        fodg_shape_plus_text_times_page(_EMPTY),
        fodg_shape_plus_text_times_page(_MINIMAL),
        fodg_shape_plus_text_times_page(_SHAPES),
    }
    assert len(vals) == 3


# fodg_is_empty_drawing
def test_is_empty_drawing_empty_true():
    assert fodg_is_empty_drawing(_EMPTY) is True

def test_is_empty_drawing_minimal_false():
    assert fodg_is_empty_drawing(_MINIMAL) is False

def test_is_empty_drawing_shapes_false():
    assert fodg_is_empty_drawing(_SHAPES) is False

def test_is_empty_drawing_returns_bool():
    assert isinstance(fodg_is_empty_drawing(_EMPTY), bool)

def test_is_empty_drawing_both_branches():
    assert fodg_is_empty_drawing(_EMPTY) is True
    assert fodg_is_empty_drawing(_SHAPES) is False

def test_is_empty_drawing_not_empty_for_shapes():
    assert not fodg_is_empty_drawing(_SHAPES)
