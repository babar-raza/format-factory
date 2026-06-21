"""
Sprint r374: FODG analytics tests.
fodg_text_count_times_three_plus_page_count + fodg_page_count_greater_than_shape_count
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import (
    fodg_text_count_times_three_plus_page_count,
    fodg_page_count_greater_than_shape_count,
)

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_text_count_times_three_plus_page_count
# empty: 0*3+1=1, minimal: 1*3+1=4, shapes: 2*3+1=7
def test_tctppc_empty():
    assert fodg_text_count_times_three_plus_page_count(_EMPTY) == 1

def test_tctppc_minimal():
    assert fodg_text_count_times_three_plus_page_count(_MINIMAL) == 4

def test_tctppc_shapes():
    assert fodg_text_count_times_three_plus_page_count(_SHAPES) == 7

def test_tctppc_empty_type():
    assert isinstance(fodg_text_count_times_three_plus_page_count(_EMPTY), int)

def test_tctppc_minimal_type():
    assert isinstance(fodg_text_count_times_three_plus_page_count(_MINIMAL), int)

def test_tctppc_shapes_type():
    assert isinstance(fodg_text_count_times_three_plus_page_count(_SHAPES), int)

def test_tctppc_empty_nonneg():
    assert fodg_text_count_times_three_plus_page_count(_EMPTY) >= 0

def test_tctppc_empty_not_minimal():
    assert fodg_text_count_times_three_plus_page_count(_EMPTY) != fodg_text_count_times_three_plus_page_count(_MINIMAL)

def test_tctppc_empty_not_shapes():
    assert fodg_text_count_times_three_plus_page_count(_EMPTY) != fodg_text_count_times_three_plus_page_count(_SHAPES)

def test_tctppc_minimal_not_shapes():
    assert fodg_text_count_times_three_plus_page_count(_MINIMAL) != fodg_text_count_times_three_plus_page_count(_SHAPES)

def test_tctppc_shapes_greatest():
    v_e = fodg_text_count_times_three_plus_page_count(_EMPTY)
    v_m = fodg_text_count_times_three_plus_page_count(_MINIMAL)
    v_s = fodg_text_count_times_three_plus_page_count(_SHAPES)
    assert v_s > v_m > v_e

def test_tctppc_empty_one():
    assert fodg_text_count_times_three_plus_page_count(_EMPTY) == 1


# fodg_page_count_greater_than_shape_count
# empty: 1>0=True, minimal: 1>1=False, shapes: 1>3=False
def test_pcgsc_empty():
    assert fodg_page_count_greater_than_shape_count(_EMPTY) is True

def test_pcgsc_minimal():
    assert fodg_page_count_greater_than_shape_count(_MINIMAL) is False

def test_pcgsc_shapes():
    assert fodg_page_count_greater_than_shape_count(_SHAPES) is False

def test_pcgsc_empty_type():
    assert isinstance(fodg_page_count_greater_than_shape_count(_EMPTY), bool)

def test_pcgsc_minimal_type():
    assert isinstance(fodg_page_count_greater_than_shape_count(_MINIMAL), bool)

def test_pcgsc_shapes_type():
    assert isinstance(fodg_page_count_greater_than_shape_count(_SHAPES), bool)

def test_pcgsc_empty_true():
    assert fodg_page_count_greater_than_shape_count(_EMPTY)

def test_pcgsc_minimal_false():
    assert not fodg_page_count_greater_than_shape_count(_MINIMAL)

def test_pcgsc_shapes_false():
    assert not fodg_page_count_greater_than_shape_count(_SHAPES)

def test_pcgsc_minimal_shapes_same():
    assert fodg_page_count_greater_than_shape_count(_MINIMAL) == fodg_page_count_greater_than_shape_count(_SHAPES)

def test_pcgsc_empty_differs_minimal():
    assert fodg_page_count_greater_than_shape_count(_EMPTY) != fodg_page_count_greater_than_shape_count(_MINIMAL)

def test_pcgsc_empty_differs_shapes():
    assert fodg_page_count_greater_than_shape_count(_EMPTY) != fodg_page_count_greater_than_shape_count(_SHAPES)
