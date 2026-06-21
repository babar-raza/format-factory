"""
Sprint r357: fodg_shape_count_times_page_count_times_two + fodg_text_count_is_positive tests.
empty-page.fodg:      shapes=0, pages=1, text=0 → 0*1*2=0;  text>0=False
minimal-drawing.fodg: shapes=1, pages=1, text=1 → 1*1*2=2;  text>0=True
shapes-basic.fodg:    shapes=3, pages=1, text=2 → 3*1*2=6;  text>0=True
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import (
    fodg_shape_count_times_page_count_times_two,
    fodg_text_count_is_positive,
)

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_shape_count_times_page_count_times_two
def test_shape_times_page_times_two_empty():
    assert fodg_shape_count_times_page_count_times_two(_EMPTY) == 0

def test_shape_times_page_times_two_minimal():
    assert fodg_shape_count_times_page_count_times_two(_MINIMAL) == 2

def test_shape_times_page_times_two_shapes():
    assert fodg_shape_count_times_page_count_times_two(_SHAPES) == 6

def test_shape_times_page_times_two_returns_int():
    assert isinstance(fodg_shape_count_times_page_count_times_two(_EMPTY), int)

def test_shape_times_page_times_two_nonnegative():
    assert fodg_shape_count_times_page_count_times_two(_EMPTY) >= 0

def test_shape_times_page_times_two_distinct():
    vals = {
        fodg_shape_count_times_page_count_times_two(_EMPTY),
        fodg_shape_count_times_page_count_times_two(_MINIMAL),
        fodg_shape_count_times_page_count_times_two(_SHAPES),
    }
    assert len(vals) == 3


# fodg_text_count_is_positive
def test_text_count_is_positive_empty_false():
    assert fodg_text_count_is_positive(_EMPTY) is False

def test_text_count_is_positive_minimal_true():
    assert fodg_text_count_is_positive(_MINIMAL) is True

def test_text_count_is_positive_shapes_true():
    assert fodg_text_count_is_positive(_SHAPES) is True

def test_text_count_is_positive_returns_bool():
    assert isinstance(fodg_text_count_is_positive(_EMPTY), bool)

def test_text_count_is_positive_both_branches():
    assert fodg_text_count_is_positive(_MINIMAL) is True
    assert fodg_text_count_is_positive(_EMPTY) is False

def test_text_count_is_positive_empty_no():
    assert not fodg_text_count_is_positive(_EMPTY)
