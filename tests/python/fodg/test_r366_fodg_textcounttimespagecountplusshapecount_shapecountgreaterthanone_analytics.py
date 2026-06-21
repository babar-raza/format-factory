"""
Sprint r366: FODG analytics tests.
fodg_text_count_times_page_count_plus_shape_count + fodg_shape_count_greater_than_one
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import (
    fodg_text_count_times_page_count_plus_shape_count,
    fodg_shape_count_greater_than_one,
)

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_text_count_times_page_count_plus_shape_count
def test_text_times_page_plus_shape_empty():
    assert fodg_text_count_times_page_count_plus_shape_count(_EMPTY) == 0

def test_text_times_page_plus_shape_minimal():
    assert fodg_text_count_times_page_count_plus_shape_count(_MINIMAL) == 2

def test_text_times_page_plus_shape_shapes():
    assert fodg_text_count_times_page_count_plus_shape_count(_SHAPES) == 5

def test_text_times_page_plus_shape_empty_type():
    assert isinstance(fodg_text_count_times_page_count_plus_shape_count(_EMPTY), int)

def test_text_times_page_plus_shape_minimal_type():
    assert isinstance(fodg_text_count_times_page_count_plus_shape_count(_MINIMAL), int)

def test_text_times_page_plus_shape_shapes_type():
    assert isinstance(fodg_text_count_times_page_count_plus_shape_count(_SHAPES), int)

def test_text_times_page_plus_shape_empty_nonneg():
    assert fodg_text_count_times_page_count_plus_shape_count(_EMPTY) >= 0

def test_text_times_page_plus_shape_empty_not_minimal():
    assert fodg_text_count_times_page_count_plus_shape_count(_EMPTY) != fodg_text_count_times_page_count_plus_shape_count(_MINIMAL)

def test_text_times_page_plus_shape_empty_not_shapes():
    assert fodg_text_count_times_page_count_plus_shape_count(_EMPTY) != fodg_text_count_times_page_count_plus_shape_count(_SHAPES)

def test_text_times_page_plus_shape_minimal_not_shapes():
    assert fodg_text_count_times_page_count_plus_shape_count(_MINIMAL) != fodg_text_count_times_page_count_plus_shape_count(_SHAPES)

def test_text_times_page_plus_shape_shapes_greatest():
    v_e = fodg_text_count_times_page_count_plus_shape_count(_EMPTY)
    v_m = fodg_text_count_times_page_count_plus_shape_count(_MINIMAL)
    v_s = fodg_text_count_times_page_count_plus_shape_count(_SHAPES)
    assert v_s > v_m > v_e

def test_text_times_page_plus_shape_empty_zero():
    assert fodg_text_count_times_page_count_plus_shape_count(_EMPTY) == 0


# fodg_shape_count_greater_than_one
def test_shape_gt_one_empty():
    assert fodg_shape_count_greater_than_one(_EMPTY) is False

def test_shape_gt_one_minimal():
    assert fodg_shape_count_greater_than_one(_MINIMAL) is False

def test_shape_gt_one_shapes():
    assert fodg_shape_count_greater_than_one(_SHAPES) is True

def test_shape_gt_one_empty_type():
    assert isinstance(fodg_shape_count_greater_than_one(_EMPTY), bool)

def test_shape_gt_one_minimal_type():
    assert isinstance(fodg_shape_count_greater_than_one(_MINIMAL), bool)

def test_shape_gt_one_shapes_type():
    assert isinstance(fodg_shape_count_greater_than_one(_SHAPES), bool)

def test_shape_gt_one_empty_false():
    assert not fodg_shape_count_greater_than_one(_EMPTY)

def test_shape_gt_one_minimal_false():
    assert not fodg_shape_count_greater_than_one(_MINIMAL)

def test_shape_gt_one_shapes_true():
    assert fodg_shape_count_greater_than_one(_SHAPES)

def test_shape_gt_one_empty_minimal_same():
    assert fodg_shape_count_greater_than_one(_EMPTY) == fodg_shape_count_greater_than_one(_MINIMAL)

def test_shape_gt_one_shapes_differs_empty():
    assert fodg_shape_count_greater_than_one(_SHAPES) != fodg_shape_count_greater_than_one(_EMPTY)

def test_shape_gt_one_shapes_differs_minimal():
    assert fodg_shape_count_greater_than_one(_SHAPES) != fodg_shape_count_greater_than_one(_MINIMAL)
