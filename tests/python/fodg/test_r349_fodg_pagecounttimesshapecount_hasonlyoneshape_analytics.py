"""
Sprint r349: fodg_page_count_times_shape_count + fodg_has_only_one_shape tests.
empty-page.fodg:       pages=1, shapes=0 → product=0;  one_shape=False
minimal-drawing.fodg:  pages=1, shapes=1 → product=1;  one_shape=True
shapes-basic.fodg:     pages=1, shapes=3 → product=3;  one_shape=False
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import fodg_page_count_times_shape_count, fodg_has_only_one_shape

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_page_count_times_shape_count
def test_page_times_shape_empty():
    assert fodg_page_count_times_shape_count(_EMPTY) == 0

def test_page_times_shape_minimal():
    assert fodg_page_count_times_shape_count(_MINIMAL) == 1

def test_page_times_shape_shapes():
    assert fodg_page_count_times_shape_count(_SHAPES) == 3

def test_page_times_shape_returns_int():
    assert isinstance(fodg_page_count_times_shape_count(_EMPTY), int)

def test_page_times_shape_nonnegative():
    assert fodg_page_count_times_shape_count(_EMPTY) >= 0

def test_page_times_shape_distinct_values():
    vals = {
        fodg_page_count_times_shape_count(_EMPTY),
        fodg_page_count_times_shape_count(_MINIMAL),
        fodg_page_count_times_shape_count(_SHAPES),
    }
    assert len(vals) == 3


# fodg_has_only_one_shape
def test_has_only_one_shape_empty_false():
    assert fodg_has_only_one_shape(_EMPTY) is False

def test_has_only_one_shape_minimal_true():
    assert fodg_has_only_one_shape(_MINIMAL) is True

def test_has_only_one_shape_shapes_false():
    assert fodg_has_only_one_shape(_SHAPES) is False

def test_has_only_one_shape_returns_bool():
    assert isinstance(fodg_has_only_one_shape(_EMPTY), bool)

def test_has_only_one_shape_both_branches():
    assert fodg_has_only_one_shape(_MINIMAL) is True
    assert fodg_has_only_one_shape(_SHAPES) is False

def test_has_only_one_shape_empty_is_false():
    assert not fodg_has_only_one_shape(_EMPTY)
