"""Sprint 578 FODG analytics deepening tests - primes 1123, 1129."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"

def test_mod1123_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1123_times_8800_plus_shape_times_283_plus_text_times_280_plus_page_times_286
    assert fodg_file_size_mod_1123_times_8800_plus_shape_times_283_plus_text_times_280_plus_page_times_286(str(EMPTY)) == 9266686

def test_mod1123_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1123_times_8800_plus_shape_times_283_plus_text_times_280_plus_page_times_286
    assert fodg_file_size_mod_1123_times_8800_plus_shape_times_283_plus_text_times_280_plus_page_times_286(str(MINIMAL)) == 3080849

def test_mod1123_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1123_times_8800_plus_shape_times_283_plus_text_times_280_plus_page_times_286
    assert fodg_file_size_mod_1123_times_8800_plus_shape_times_283_plus_text_times_280_plus_page_times_286(str(SHAPES)) == 4445695

def test_mod1129_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1129_times_8900_plus_shape_times_285_plus_text_times_282_plus_page_times_288
    assert fodg_file_size_mod_1129_times_8900_plus_shape_times_285_plus_text_times_282_plus_page_times_288(str(EMPTY)) == 9371988

def test_mod1129_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1129_times_8900_plus_shape_times_285_plus_text_times_282_plus_page_times_288
    assert fodg_file_size_mod_1129_times_8900_plus_shape_times_285_plus_text_times_282_plus_page_times_288(str(MINIMAL)) == 3062455

def test_mod1129_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1129_times_8900_plus_shape_times_285_plus_text_times_282_plus_page_times_288
    assert fodg_file_size_mod_1129_times_8900_plus_shape_times_285_plus_text_times_282_plus_page_times_288(str(SHAPES)) == 4442807

def test_mod1123_empty_positive():
    from fodg.fodg_analytics import fodg_file_size_mod_1123_times_8800_plus_shape_times_283_plus_text_times_280_plus_page_times_286
    assert fodg_file_size_mod_1123_times_8800_plus_shape_times_283_plus_text_times_280_plus_page_times_286(str(EMPTY)) > 0

def test_mod1129_empty_positive():
    from fodg.fodg_analytics import fodg_file_size_mod_1129_times_8900_plus_shape_times_285_plus_text_times_282_plus_page_times_288
    assert fodg_file_size_mod_1129_times_8900_plus_shape_times_285_plus_text_times_282_plus_page_times_288(str(EMPTY)) > 0

def test_mod1123_neq_mod1129_shapes():
    from fodg.fodg_analytics import (
        fodg_file_size_mod_1123_times_8800_plus_shape_times_283_plus_text_times_280_plus_page_times_286,
        fodg_file_size_mod_1129_times_8900_plus_shape_times_285_plus_text_times_282_plus_page_times_288,
    )
    assert fodg_file_size_mod_1123_times_8800_plus_shape_times_283_plus_text_times_280_plus_page_times_286(str(SHAPES)) != fodg_file_size_mod_1129_times_8900_plus_shape_times_285_plus_text_times_282_plus_page_times_288(str(SHAPES))

def test_mod1123_consistent():
    from fodg.fodg_analytics import fodg_file_size_mod_1123_times_8800_plus_shape_times_283_plus_text_times_280_plus_page_times_286
    assert fodg_file_size_mod_1123_times_8800_plus_shape_times_283_plus_text_times_280_plus_page_times_286(str(MINIMAL)) == fodg_file_size_mod_1123_times_8800_plus_shape_times_283_plus_text_times_280_plus_page_times_286(str(MINIMAL))
