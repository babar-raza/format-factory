"""Sprint 608 FODG analytics deepening tests - primes 1283, 1289."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"

def test_mod1283_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1283_times_10800_plus_shape_times_323_plus_text_times_320_plus_page_times_326
    assert fodg_file_size_mod_1283_times_10800_plus_shape_times_323_plus_text_times_320_plus_page_times_326(str(EMPTY)) == 11372726

def test_mod1283_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1283_times_10800_plus_shape_times_323_plus_text_times_320_plus_page_times_326
    assert fodg_file_size_mod_1283_times_10800_plus_shape_times_323_plus_text_times_320_plus_page_times_326(str(MINIMAL)) == 2052969

def test_mod1283_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1283_times_10800_plus_shape_times_323_plus_text_times_320_plus_page_times_326
    assert fodg_file_size_mod_1283_times_10800_plus_shape_times_323_plus_text_times_320_plus_page_times_326(str(SHAPES)) == 3727935

def test_mod1289_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1289_times_10900_plus_shape_times_325_plus_text_times_322_plus_page_times_328
    assert fodg_file_size_mod_1289_times_10900_plus_shape_times_325_plus_text_times_322_plus_page_times_328(str(EMPTY)) == 11478028

def test_mod1289_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1289_times_10900_plus_shape_times_325_plus_text_times_322_plus_page_times_328
    assert fodg_file_size_mod_1289_times_10900_plus_shape_times_325_plus_text_times_322_plus_page_times_328(str(MINIMAL)) == 2006575

def test_mod1289_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1289_times_10900_plus_shape_times_325_plus_text_times_322_plus_page_times_328
    assert fodg_file_size_mod_1289_times_10900_plus_shape_times_325_plus_text_times_322_plus_page_times_328(str(SHAPES)) == 3697047

def test_mod1283_positive():
    from fodg.fodg_analytics import fodg_file_size_mod_1283_times_10800_plus_shape_times_323_plus_text_times_320_plus_page_times_326
    assert fodg_file_size_mod_1283_times_10800_plus_shape_times_323_plus_text_times_320_plus_page_times_326(str(EMPTY)) > 0

def test_mod1289_positive():
    from fodg.fodg_analytics import fodg_file_size_mod_1289_times_10900_plus_shape_times_325_plus_text_times_322_plus_page_times_328
    assert fodg_file_size_mod_1289_times_10900_plus_shape_times_325_plus_text_times_322_plus_page_times_328(str(EMPTY)) > 0

def test_mod1283_neq_mod1289():
    from fodg.fodg_analytics import fodg_file_size_mod_1283_times_10800_plus_shape_times_323_plus_text_times_320_plus_page_times_326, fodg_file_size_mod_1289_times_10900_plus_shape_times_325_plus_text_times_322_plus_page_times_328
    assert fodg_file_size_mod_1283_times_10800_plus_shape_times_323_plus_text_times_320_plus_page_times_326(str(SHAPES)) != fodg_file_size_mod_1289_times_10900_plus_shape_times_325_plus_text_times_322_plus_page_times_328(str(SHAPES))

def test_mod1283_consistent():
    from fodg.fodg_analytics import fodg_file_size_mod_1283_times_10800_plus_shape_times_323_plus_text_times_320_plus_page_times_326
    assert fodg_file_size_mod_1283_times_10800_plus_shape_times_323_plus_text_times_320_plus_page_times_326(str(MINIMAL)) == fodg_file_size_mod_1283_times_10800_plus_shape_times_323_plus_text_times_320_plus_page_times_326(str(MINIMAL))
