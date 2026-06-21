"""Sprint 551 FODG analytics deepening tests - primes 1013, 1019."""
import pytest
from pathlib import Path

EMPTY = Path("samples/by-format/fodg/empty-page.fodg")
MINIMAL = Path("samples/by-format/fodg/minimal-drawing.fodg")
SHAPES = Path("samples/by-format/fodg/shapes-basic.fodg")

def test_fn1_empty():
    from fodg import fodg_file_size_mod_1013_times_7000_plus_shape_times_247_plus_text_times_244_plus_page_times_250 as fn
    assert fn(str(EMPTY)) == 280250
def test_fn1_minimal():
    from fodg import fodg_file_size_mod_1013_times_7000_plus_shape_times_247_plus_text_times_244_plus_page_times_250 as fn
    assert fn(str(MINIMAL)) == 3220741
def test_fn1_shapes():
    from fodg import fodg_file_size_mod_1013_times_7000_plus_shape_times_247_plus_text_times_244_plus_page_times_250 as fn
    assert fn(str(SHAPES)) == 4306479
def test_fn1_int():
    from fodg import fodg_file_size_mod_1013_times_7000_plus_shape_times_247_plus_text_times_244_plus_page_times_250 as fn
    assert isinstance(fn(str(EMPTY)), int)
def test_fn1_nonneg():
    from fodg import fodg_file_size_mod_1013_times_7000_plus_shape_times_247_plus_text_times_244_plus_page_times_250 as fn
    for s in [EMPTY, MINIMAL, SHAPES]: assert fn(str(s)) >= 0
def test_fn1_path():
    from fodg import fodg_file_size_mod_1013_times_7000_plus_shape_times_247_plus_text_times_244_plus_page_times_250 as fn
    assert fn(EMPTY) == 280250
def test_fn1_doc():
    from fodg import fodg_file_size_mod_1013_times_7000_plus_shape_times_247_plus_text_times_244_plus_page_times_250 as fn
    assert fn.__doc__ is not None and "1013" in fn.__doc__
def test_fn2_empty():
    from fodg import fodg_file_size_mod_1019_times_7100_plus_shape_times_249_plus_text_times_246_plus_page_times_252 as fn
    assert fn(str(EMPTY)) == 241652
def test_fn2_minimal():
    from fodg import fodg_file_size_mod_1019_times_7100_plus_shape_times_249_plus_text_times_246_plus_page_times_252 as fn
    assert fn(str(MINIMAL)) == 3224147
def test_fn2_shapes():
    from fodg import fodg_file_size_mod_1019_times_7100_plus_shape_times_249_plus_text_times_246_plus_page_times_252 as fn
    assert fn(str(SHAPES)) == 4325391
def test_fn2_int():
    from fodg import fodg_file_size_mod_1019_times_7100_plus_shape_times_249_plus_text_times_246_plus_page_times_252 as fn
    assert isinstance(fn(str(EMPTY)), int)
def test_fn2_nonneg():
    from fodg import fodg_file_size_mod_1019_times_7100_plus_shape_times_249_plus_text_times_246_plus_page_times_252 as fn
    for s in [EMPTY, MINIMAL, SHAPES]: assert fn(str(s)) >= 0
def test_fn2_path():
    from fodg import fodg_file_size_mod_1019_times_7100_plus_shape_times_249_plus_text_times_246_plus_page_times_252 as fn
    assert fn(MINIMAL) == 3224147
def test_fn2_doc():
    from fodg import fodg_file_size_mod_1019_times_7100_plus_shape_times_249_plus_text_times_246_plus_page_times_252 as fn
    assert fn.__doc__ is not None and "1019" in fn.__doc__
