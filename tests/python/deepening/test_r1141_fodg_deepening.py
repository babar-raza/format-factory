"""Sprint 587 FODG analytics deepening tests - primes 1181, 1187."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"

def test_mod1181_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1181_times_9400_plus_shape_times_295_plus_text_times_292_plus_page_times_298
    assert fodg_file_size_mod_1181_times_9400_plus_shape_times_295_plus_text_times_292_plus_page_times_298(str(EMPTY)) == 9898498

def test_mod1181_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1181_times_9400_plus_shape_times_295_plus_text_times_292_plus_page_times_298
    assert fodg_file_size_mod_1181_times_9400_plus_shape_times_295_plus_text_times_292_plus_page_times_298(str(MINIMAL)) == 2745685

def test_mod1181_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1181_times_9400_plus_shape_times_295_plus_text_times_292_plus_page_times_298
    assert fodg_file_size_mod_1181_times_9400_plus_shape_times_295_plus_text_times_292_plus_page_times_298(str(SHAPES)) == 4203567

def test_mod1187_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1187_times_9500_plus_shape_times_297_plus_text_times_294_plus_page_times_300
    assert fodg_file_size_mod_1187_times_9500_plus_shape_times_297_plus_text_times_294_plus_page_times_300(str(EMPTY)) == 10003800

def test_mod1187_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1187_times_9500_plus_shape_times_297_plus_text_times_294_plus_page_times_300
    assert fodg_file_size_mod_1187_times_9500_plus_shape_times_297_plus_text_times_294_plus_page_times_300(str(MINIMAL)) == 2717891

def test_mod1187_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1187_times_9500_plus_shape_times_297_plus_text_times_294_plus_page_times_300
    assert fodg_file_size_mod_1187_times_9500_plus_shape_times_297_plus_text_times_294_plus_page_times_300(str(SHAPES)) == 4191279

def test_mod1181_positive():
    from fodg.fodg_analytics import fodg_file_size_mod_1181_times_9400_plus_shape_times_295_plus_text_times_292_plus_page_times_298
    assert fodg_file_size_mod_1181_times_9400_plus_shape_times_295_plus_text_times_292_plus_page_times_298(str(EMPTY)) > 0

def test_mod1187_positive():
    from fodg.fodg_analytics import fodg_file_size_mod_1187_times_9500_plus_shape_times_297_plus_text_times_294_plus_page_times_300
    assert fodg_file_size_mod_1187_times_9500_plus_shape_times_297_plus_text_times_294_plus_page_times_300(str(EMPTY)) > 0

def test_mod1181_neq_mod1187():
    from fodg.fodg_analytics import fodg_file_size_mod_1181_times_9400_plus_shape_times_295_plus_text_times_292_plus_page_times_298, fodg_file_size_mod_1187_times_9500_plus_shape_times_297_plus_text_times_294_plus_page_times_300
    assert fodg_file_size_mod_1181_times_9400_plus_shape_times_295_plus_text_times_292_plus_page_times_298(str(SHAPES)) != fodg_file_size_mod_1187_times_9500_plus_shape_times_297_plus_text_times_294_plus_page_times_300(str(SHAPES))

def test_mod1181_consistent():
    from fodg.fodg_analytics import fodg_file_size_mod_1181_times_9400_plus_shape_times_295_plus_text_times_292_plus_page_times_298
    assert fodg_file_size_mod_1181_times_9400_plus_shape_times_295_plus_text_times_292_plus_page_times_298(str(MINIMAL)) == fodg_file_size_mod_1181_times_9400_plus_shape_times_295_plus_text_times_292_plus_page_times_298(str(MINIMAL))
