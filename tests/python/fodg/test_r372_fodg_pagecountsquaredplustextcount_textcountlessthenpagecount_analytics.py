"""
Sprint r372: FODG analytics tests.
fodg_page_count_squared_plus_text_count + fodg_text_count_less_than_page_count
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from src.python.fodg.fodg_codec import (
    fodg_page_count_squared_plus_text_count,
    fodg_text_count_less_than_page_count,
)

_FODG = Path(__file__).resolve().parents[3] / "samples" / "by-format" / "fodg"
_EMPTY   = _FODG / "empty-page.fodg"
_MINIMAL = _FODG / "minimal-drawing.fodg"
_SHAPES  = _FODG / "shapes-basic.fodg"


# fodg_page_count_squared_plus_text_count
# empty: 1²+0=1, minimal: 1²+1=2, shapes: 1²+2=3
def test_pcsptp_empty():
    assert fodg_page_count_squared_plus_text_count(_EMPTY) == 1

def test_pcsptp_minimal():
    assert fodg_page_count_squared_plus_text_count(_MINIMAL) == 2

def test_pcsptp_shapes():
    assert fodg_page_count_squared_plus_text_count(_SHAPES) == 3

def test_pcsptp_empty_type():
    assert isinstance(fodg_page_count_squared_plus_text_count(_EMPTY), int)

def test_pcsptp_minimal_type():
    assert isinstance(fodg_page_count_squared_plus_text_count(_MINIMAL), int)

def test_pcsptp_shapes_type():
    assert isinstance(fodg_page_count_squared_plus_text_count(_SHAPES), int)

def test_pcsptp_empty_nonneg():
    assert fodg_page_count_squared_plus_text_count(_EMPTY) >= 0

def test_pcsptp_empty_not_minimal():
    assert fodg_page_count_squared_plus_text_count(_EMPTY) != fodg_page_count_squared_plus_text_count(_MINIMAL)

def test_pcsptp_empty_not_shapes():
    assert fodg_page_count_squared_plus_text_count(_EMPTY) != fodg_page_count_squared_plus_text_count(_SHAPES)

def test_pcsptp_minimal_not_shapes():
    assert fodg_page_count_squared_plus_text_count(_MINIMAL) != fodg_page_count_squared_plus_text_count(_SHAPES)

def test_pcsptp_shapes_greatest():
    v_e = fodg_page_count_squared_plus_text_count(_EMPTY)
    v_m = fodg_page_count_squared_plus_text_count(_MINIMAL)
    v_s = fodg_page_count_squared_plus_text_count(_SHAPES)
    assert v_s > v_m > v_e

def test_pcsptp_empty_one():
    assert fodg_page_count_squared_plus_text_count(_EMPTY) == 1


# fodg_text_count_less_than_page_count
# empty: 0<1=True, minimal: 1<1=False, shapes: 2<1=False
def test_tclpc_empty():
    assert fodg_text_count_less_than_page_count(_EMPTY) is True

def test_tclpc_minimal():
    assert fodg_text_count_less_than_page_count(_MINIMAL) is False

def test_tclpc_shapes():
    assert fodg_text_count_less_than_page_count(_SHAPES) is False

def test_tclpc_empty_type():
    assert isinstance(fodg_text_count_less_than_page_count(_EMPTY), bool)

def test_tclpc_minimal_type():
    assert isinstance(fodg_text_count_less_than_page_count(_MINIMAL), bool)

def test_tclpc_shapes_type():
    assert isinstance(fodg_text_count_less_than_page_count(_SHAPES), bool)

def test_tclpc_empty_true():
    assert fodg_text_count_less_than_page_count(_EMPTY)

def test_tclpc_minimal_false():
    assert not fodg_text_count_less_than_page_count(_MINIMAL)

def test_tclpc_shapes_false():
    assert not fodg_text_count_less_than_page_count(_SHAPES)

def test_tclpc_minimal_shapes_same():
    assert fodg_text_count_less_than_page_count(_MINIMAL) == fodg_text_count_less_than_page_count(_SHAPES)

def test_tclpc_empty_differs_minimal():
    assert fodg_text_count_less_than_page_count(_EMPTY) != fodg_text_count_less_than_page_count(_MINIMAL)

def test_tclpc_empty_differs_shapes():
    assert fodg_text_count_less_than_page_count(_EMPTY) != fodg_text_count_less_than_page_count(_SHAPES)
