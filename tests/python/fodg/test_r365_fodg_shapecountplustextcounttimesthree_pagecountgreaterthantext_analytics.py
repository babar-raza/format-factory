"""
Sprint r365: FODG analytics tests.
fodg_shape_count_plus_text_count_times_three + fodg_page_count_greater_than_text_count
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import (
    fodg_shape_count_plus_text_count_times_three,
    fodg_page_count_greater_than_text_count,
)

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_shape_count_plus_text_count_times_three
def test_shape_plus_text_times_three_empty():
    assert fodg_shape_count_plus_text_count_times_three(_EMPTY) == 0

def test_shape_plus_text_times_three_minimal():
    assert fodg_shape_count_plus_text_count_times_three(_MINIMAL) == 4

def test_shape_plus_text_times_three_shapes():
    assert fodg_shape_count_plus_text_count_times_three(_SHAPES) == 9

def test_shape_plus_text_times_three_empty_type():
    assert isinstance(fodg_shape_count_plus_text_count_times_three(_EMPTY), int)

def test_shape_plus_text_times_three_minimal_type():
    assert isinstance(fodg_shape_count_plus_text_count_times_three(_MINIMAL), int)

def test_shape_plus_text_times_three_shapes_type():
    assert isinstance(fodg_shape_count_plus_text_count_times_three(_SHAPES), int)

def test_shape_plus_text_times_three_empty_nonneg():
    assert fodg_shape_count_plus_text_count_times_three(_EMPTY) >= 0

def test_shape_plus_text_times_three_empty_not_minimal():
    assert fodg_shape_count_plus_text_count_times_three(_EMPTY) != fodg_shape_count_plus_text_count_times_three(_MINIMAL)

def test_shape_plus_text_times_three_empty_not_shapes():
    assert fodg_shape_count_plus_text_count_times_three(_EMPTY) != fodg_shape_count_plus_text_count_times_three(_SHAPES)

def test_shape_plus_text_times_three_minimal_not_shapes():
    assert fodg_shape_count_plus_text_count_times_three(_MINIMAL) != fodg_shape_count_plus_text_count_times_three(_SHAPES)

def test_shape_plus_text_times_three_shapes_greatest():
    v_e = fodg_shape_count_plus_text_count_times_three(_EMPTY)
    v_m = fodg_shape_count_plus_text_count_times_three(_MINIMAL)
    v_s = fodg_shape_count_plus_text_count_times_three(_SHAPES)
    assert v_s > v_m > v_e

def test_shape_plus_text_times_three_empty_zero():
    assert fodg_shape_count_plus_text_count_times_three(_EMPTY) == 0


# fodg_page_count_greater_than_text_count
def test_page_gt_text_empty():
    assert fodg_page_count_greater_than_text_count(_EMPTY) is True

def test_page_gt_text_minimal():
    assert fodg_page_count_greater_than_text_count(_MINIMAL) is False

def test_page_gt_text_shapes():
    assert fodg_page_count_greater_than_text_count(_SHAPES) is False

def test_page_gt_text_empty_type():
    assert isinstance(fodg_page_count_greater_than_text_count(_EMPTY), bool)

def test_page_gt_text_minimal_type():
    assert isinstance(fodg_page_count_greater_than_text_count(_MINIMAL), bool)

def test_page_gt_text_shapes_type():
    assert isinstance(fodg_page_count_greater_than_text_count(_SHAPES), bool)

def test_page_gt_text_empty_true():
    assert fodg_page_count_greater_than_text_count(_EMPTY)

def test_page_gt_text_minimal_false():
    assert not fodg_page_count_greater_than_text_count(_MINIMAL)

def test_page_gt_text_shapes_false():
    assert not fodg_page_count_greater_than_text_count(_SHAPES)

def test_page_gt_text_empty_differs_minimal():
    assert fodg_page_count_greater_than_text_count(_EMPTY) != fodg_page_count_greater_than_text_count(_MINIMAL)

def test_page_gt_text_empty_differs_shapes():
    assert fodg_page_count_greater_than_text_count(_EMPTY) != fodg_page_count_greater_than_text_count(_SHAPES)

def test_page_gt_text_minimal_shapes_same():
    assert fodg_page_count_greater_than_text_count(_MINIMAL) == fodg_page_count_greater_than_text_count(_SHAPES)
