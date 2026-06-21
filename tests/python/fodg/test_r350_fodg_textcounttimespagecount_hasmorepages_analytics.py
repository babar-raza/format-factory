"""
Sprint r350: fodg_text_count_times_page_count + fodg_has_more_pages_than_shapes tests.
empty-page.fodg:       text=0, pages=1 → 0;  pages(1)>shapes(0) → True
minimal-drawing.fodg:  text=1, pages=1 → 1;  pages(1)>shapes(1) → False
shapes-basic.fodg:     text=2, pages=1 → 2;  pages(1)>shapes(3) → False
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import fodg_text_count_times_page_count, fodg_has_more_pages_than_shapes

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_text_count_times_page_count
def test_text_times_page_empty():
    assert fodg_text_count_times_page_count(_EMPTY) == 0

def test_text_times_page_minimal():
    assert fodg_text_count_times_page_count(_MINIMAL) == 1

def test_text_times_page_shapes():
    assert fodg_text_count_times_page_count(_SHAPES) == 2

def test_text_times_page_returns_int():
    assert isinstance(fodg_text_count_times_page_count(_EMPTY), int)

def test_text_times_page_nonnegative():
    assert fodg_text_count_times_page_count(_EMPTY) >= 0

def test_text_times_page_distinct_values():
    vals = {
        fodg_text_count_times_page_count(_EMPTY),
        fodg_text_count_times_page_count(_MINIMAL),
        fodg_text_count_times_page_count(_SHAPES),
    }
    assert len(vals) == 3


# fodg_has_more_pages_than_shapes
def test_has_more_pages_than_shapes_empty_true():
    assert fodg_has_more_pages_than_shapes(_EMPTY) is True

def test_has_more_pages_than_shapes_minimal_false():
    assert fodg_has_more_pages_than_shapes(_MINIMAL) is False

def test_has_more_pages_than_shapes_shapes_false():
    assert fodg_has_more_pages_than_shapes(_SHAPES) is False

def test_has_more_pages_than_shapes_returns_bool():
    assert isinstance(fodg_has_more_pages_than_shapes(_EMPTY), bool)

def test_has_more_pages_than_shapes_both_branches():
    assert fodg_has_more_pages_than_shapes(_EMPTY) is True
    assert fodg_has_more_pages_than_shapes(_SHAPES) is False

def test_has_more_pages_than_shapes_full_drawing_false():
    assert not fodg_has_more_pages_than_shapes(_SHAPES)
