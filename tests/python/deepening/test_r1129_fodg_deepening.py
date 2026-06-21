"""Sprint 575 FODG analytics deepening tests - primes 1109, 1117."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"

def test_mod1109_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1109_times_8600_plus_shape_times_279_plus_text_times_276_plus_page_times_282
    assert fodg_file_size_mod_1109_times_8600_plus_shape_times_279_plus_text_times_276_plus_page_times_282(str(EMPTY)) == 9056082

def test_mod1109_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1109_times_8600_plus_shape_times_279_plus_text_times_276_plus_page_times_282
    assert fodg_file_size_mod_1109_times_8600_plus_shape_times_279_plus_text_times_276_plus_page_times_282(str(MINIMAL)) == 3131237

def test_mod1109_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1109_times_8600_plus_shape_times_279_plus_text_times_276_plus_page_times_282
    assert fodg_file_size_mod_1109_times_8600_plus_shape_times_279_plus_text_times_276_plus_page_times_282(str(SHAPES)) == 4465071

def test_mod1117_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1117_times_8700_plus_shape_times_281_plus_text_times_278_plus_page_times_284
    assert fodg_file_size_mod_1117_times_8700_plus_shape_times_281_plus_text_times_278_plus_page_times_284(str(EMPTY)) == 9161384

def test_mod1117_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1117_times_8700_plus_shape_times_281_plus_text_times_278_plus_page_times_284
    assert fodg_file_size_mod_1117_times_8700_plus_shape_times_281_plus_text_times_278_plus_page_times_284(str(MINIMAL)) == 3098043

def test_mod1117_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1117_times_8700_plus_shape_times_281_plus_text_times_278_plus_page_times_284
    assert fodg_file_size_mod_1117_times_8700_plus_shape_times_281_plus_text_times_278_plus_page_times_284(str(SHAPES)) == 4447383

def test_mod1109_empty_positive():
    from fodg.fodg_analytics import fodg_file_size_mod_1109_times_8600_plus_shape_times_279_plus_text_times_276_plus_page_times_282
    assert fodg_file_size_mod_1109_times_8600_plus_shape_times_279_plus_text_times_276_plus_page_times_282(str(EMPTY)) > 0

def test_mod1117_empty_positive():
    from fodg.fodg_analytics import fodg_file_size_mod_1117_times_8700_plus_shape_times_281_plus_text_times_278_plus_page_times_284
    assert fodg_file_size_mod_1117_times_8700_plus_shape_times_281_plus_text_times_278_plus_page_times_284(str(EMPTY)) > 0

def test_mod1109_neq_mod1117_shapes():
    from fodg.fodg_analytics import (
        fodg_file_size_mod_1109_times_8600_plus_shape_times_279_plus_text_times_276_plus_page_times_282,
        fodg_file_size_mod_1117_times_8700_plus_shape_times_281_plus_text_times_278_plus_page_times_284,
    )
    assert fodg_file_size_mod_1109_times_8600_plus_shape_times_279_plus_text_times_276_plus_page_times_282(str(SHAPES)) != fodg_file_size_mod_1117_times_8700_plus_shape_times_281_plus_text_times_278_plus_page_times_284(str(SHAPES))

def test_mod1109_consistent():
    from fodg.fodg_analytics import fodg_file_size_mod_1109_times_8600_plus_shape_times_279_plus_text_times_276_plus_page_times_282
    assert fodg_file_size_mod_1109_times_8600_plus_shape_times_279_plus_text_times_276_plus_page_times_282(str(MINIMAL)) == fodg_file_size_mod_1109_times_8600_plus_shape_times_279_plus_text_times_276_plus_page_times_282(str(MINIMAL))
