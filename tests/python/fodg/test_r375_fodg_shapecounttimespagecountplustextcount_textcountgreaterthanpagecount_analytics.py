"""
Sprint r375: FODG analytics tests.
fodg_shape_count_times_page_count_plus_text_count + fodg_text_count_greater_than_page_count
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import (
    fodg_shape_count_times_page_count_plus_text_count,
    fodg_text_count_greater_than_page_count,
)

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_shape_count_times_page_count_plus_text_count
# empty: 0*1+0=0, minimal: 1*1+1=2, shapes: 3*1+2=5
def test_sctpcptc_empty():
    assert fodg_shape_count_times_page_count_plus_text_count(_EMPTY) == 0

def test_sctpcptc_minimal():
    assert fodg_shape_count_times_page_count_plus_text_count(_MINIMAL) == 2

def test_sctpcptc_shapes():
    assert fodg_shape_count_times_page_count_plus_text_count(_SHAPES) == 5

def test_sctpcptc_empty_type():
    assert isinstance(fodg_shape_count_times_page_count_plus_text_count(_EMPTY), int)

def test_sctpcptc_minimal_type():
    assert isinstance(fodg_shape_count_times_page_count_plus_text_count(_MINIMAL), int)

def test_sctpcptc_shapes_type():
    assert isinstance(fodg_shape_count_times_page_count_plus_text_count(_SHAPES), int)

def test_sctpcptc_empty_zero():
    assert fodg_shape_count_times_page_count_plus_text_count(_EMPTY) == 0

def test_sctpcptc_empty_not_minimal():
    assert fodg_shape_count_times_page_count_plus_text_count(_EMPTY) != fodg_shape_count_times_page_count_plus_text_count(_MINIMAL)

def test_sctpcptc_empty_not_shapes():
    assert fodg_shape_count_times_page_count_plus_text_count(_EMPTY) != fodg_shape_count_times_page_count_plus_text_count(_SHAPES)

def test_sctpcptc_minimal_not_shapes():
    assert fodg_shape_count_times_page_count_plus_text_count(_MINIMAL) != fodg_shape_count_times_page_count_plus_text_count(_SHAPES)

def test_sctpcptc_shapes_greatest():
    v_e = fodg_shape_count_times_page_count_plus_text_count(_EMPTY)
    v_m = fodg_shape_count_times_page_count_plus_text_count(_MINIMAL)
    v_s = fodg_shape_count_times_page_count_plus_text_count(_SHAPES)
    assert v_s > v_m > v_e

def test_sctpcptc_shapes_five():
    assert fodg_shape_count_times_page_count_plus_text_count(_SHAPES) == 5


# fodg_text_count_greater_than_page_count
# empty: 0>1=False, minimal: 1>1=False, shapes: 2>1=True
def test_tcgpc_empty():
    assert fodg_text_count_greater_than_page_count(_EMPTY) is False

def test_tcgpc_minimal():
    assert fodg_text_count_greater_than_page_count(_MINIMAL) is False

def test_tcgpc_shapes():
    assert fodg_text_count_greater_than_page_count(_SHAPES) is True

def test_tcgpc_empty_type():
    assert isinstance(fodg_text_count_greater_than_page_count(_EMPTY), bool)

def test_tcgpc_minimal_type():
    assert isinstance(fodg_text_count_greater_than_page_count(_MINIMAL), bool)

def test_tcgpc_shapes_type():
    assert isinstance(fodg_text_count_greater_than_page_count(_SHAPES), bool)

def test_tcgpc_empty_false():
    assert not fodg_text_count_greater_than_page_count(_EMPTY)

def test_tcgpc_minimal_false():
    assert not fodg_text_count_greater_than_page_count(_MINIMAL)

def test_tcgpc_shapes_true():
    assert fodg_text_count_greater_than_page_count(_SHAPES)

def test_tcgpc_empty_minimal_same():
    assert fodg_text_count_greater_than_page_count(_EMPTY) == fodg_text_count_greater_than_page_count(_MINIMAL)

def test_tcgpc_shapes_differs_empty():
    assert fodg_text_count_greater_than_page_count(_SHAPES) != fodg_text_count_greater_than_page_count(_EMPTY)

def test_tcgpc_shapes_differs_minimal():
    assert fodg_text_count_greater_than_page_count(_SHAPES) != fodg_text_count_greater_than_page_count(_MINIMAL)
