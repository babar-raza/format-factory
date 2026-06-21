"""
Sprint r373: FODG analytics tests.
fodg_shape_count_times_two_plus_page_count + fodg_shape_count_not_equal_text_count
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import (
    fodg_shape_count_times_two_plus_page_count,
    fodg_shape_count_not_equal_text_count,
)

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_shape_count_times_two_plus_page_count
# empty: 0*2+1=1, minimal: 1*2+1=3, shapes: 3*2+1=7
def test_sctppc_empty():
    assert fodg_shape_count_times_two_plus_page_count(_EMPTY) == 1

def test_sctppc_minimal():
    assert fodg_shape_count_times_two_plus_page_count(_MINIMAL) == 3

def test_sctppc_shapes():
    assert fodg_shape_count_times_two_plus_page_count(_SHAPES) == 7

def test_sctppc_empty_type():
    assert isinstance(fodg_shape_count_times_two_plus_page_count(_EMPTY), int)

def test_sctppc_minimal_type():
    assert isinstance(fodg_shape_count_times_two_plus_page_count(_MINIMAL), int)

def test_sctppc_shapes_type():
    assert isinstance(fodg_shape_count_times_two_plus_page_count(_SHAPES), int)

def test_sctppc_empty_nonneg():
    assert fodg_shape_count_times_two_plus_page_count(_EMPTY) >= 0

def test_sctppc_empty_not_minimal():
    assert fodg_shape_count_times_two_plus_page_count(_EMPTY) != fodg_shape_count_times_two_plus_page_count(_MINIMAL)

def test_sctppc_empty_not_shapes():
    assert fodg_shape_count_times_two_plus_page_count(_EMPTY) != fodg_shape_count_times_two_plus_page_count(_SHAPES)

def test_sctppc_minimal_not_shapes():
    assert fodg_shape_count_times_two_plus_page_count(_MINIMAL) != fodg_shape_count_times_two_plus_page_count(_SHAPES)

def test_sctppc_shapes_greatest():
    v_e = fodg_shape_count_times_two_plus_page_count(_EMPTY)
    v_m = fodg_shape_count_times_two_plus_page_count(_MINIMAL)
    v_s = fodg_shape_count_times_two_plus_page_count(_SHAPES)
    assert v_s > v_m > v_e

def test_sctppc_empty_one():
    assert fodg_shape_count_times_two_plus_page_count(_EMPTY) == 1


# fodg_shape_count_not_equal_text_count
# empty: 0≠0=False, minimal: 1≠1=False, shapes: 3≠2=True
def test_scntc_empty():
    assert fodg_shape_count_not_equal_text_count(_EMPTY) is False

def test_scntc_minimal():
    assert fodg_shape_count_not_equal_text_count(_MINIMAL) is False

def test_scntc_shapes():
    assert fodg_shape_count_not_equal_text_count(_SHAPES) is True

def test_scntc_empty_type():
    assert isinstance(fodg_shape_count_not_equal_text_count(_EMPTY), bool)

def test_scntc_minimal_type():
    assert isinstance(fodg_shape_count_not_equal_text_count(_MINIMAL), bool)

def test_scntc_shapes_type():
    assert isinstance(fodg_shape_count_not_equal_text_count(_SHAPES), bool)

def test_scntc_empty_false():
    assert not fodg_shape_count_not_equal_text_count(_EMPTY)

def test_scntc_minimal_false():
    assert not fodg_shape_count_not_equal_text_count(_MINIMAL)

def test_scntc_shapes_true():
    assert fodg_shape_count_not_equal_text_count(_SHAPES)

def test_scntc_empty_minimal_same():
    assert fodg_shape_count_not_equal_text_count(_EMPTY) == fodg_shape_count_not_equal_text_count(_MINIMAL)

def test_scntc_shapes_differs_empty():
    assert fodg_shape_count_not_equal_text_count(_SHAPES) != fodg_shape_count_not_equal_text_count(_EMPTY)

def test_scntc_shapes_differs_minimal():
    assert fodg_shape_count_not_equal_text_count(_SHAPES) != fodg_shape_count_not_equal_text_count(_MINIMAL)
