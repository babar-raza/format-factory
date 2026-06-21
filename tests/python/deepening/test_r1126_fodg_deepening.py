"""Sprint 572 FODG analytics deepening tests - primes 1097, 1103."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"

def test_mod1097_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1097_times_8400_plus_shape_times_275_plus_text_times_272_plus_page_times_278
    assert fodg_file_size_mod_1097_times_8400_plus_shape_times_275_plus_text_times_272_plus_page_times_278(str(EMPTY)) == 8845478

def test_mod1097_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1097_times_8400_plus_shape_times_275_plus_text_times_272_plus_page_times_278
    assert fodg_file_size_mod_1097_times_8400_plus_shape_times_275_plus_text_times_272_plus_page_times_278(str(MINIMAL)) == 3159225

def test_mod1097_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1097_times_8400_plus_shape_times_275_plus_text_times_272_plus_page_times_278
    assert fodg_file_size_mod_1097_times_8400_plus_shape_times_275_plus_text_times_272_plus_page_times_278(str(SHAPES)) == 4462047

def test_mod1103_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1103_times_8500_plus_shape_times_277_plus_text_times_274_plus_page_times_280
    assert fodg_file_size_mod_1103_times_8500_plus_shape_times_277_plus_text_times_274_plus_page_times_280(str(EMPTY)) == 8950780

def test_mod1103_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1103_times_8500_plus_shape_times_277_plus_text_times_274_plus_page_times_280
    assert fodg_file_size_mod_1103_times_8500_plus_shape_times_277_plus_text_times_274_plus_page_times_280(str(MINIMAL)) == 3145831

def test_mod1103_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1103_times_8500_plus_shape_times_277_plus_text_times_274_plus_page_times_280
    assert fodg_file_size_mod_1103_times_8500_plus_shape_times_277_plus_text_times_274_plus_page_times_280(str(SHAPES)) == 4464159

def test_mod1097_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1097_times_8400_plus_shape_times_275_plus_text_times_272_plus_page_times_278
    assert isinstance(fodg_file_size_mod_1097_times_8400_plus_shape_times_275_plus_text_times_272_plus_page_times_278(str(EMPTY)), int)

def test_mod1097_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1097_times_8400_plus_shape_times_275_plus_text_times_272_plus_page_times_278
    assert fodg_file_size_mod_1097_times_8400_plus_shape_times_275_plus_text_times_272_plus_page_times_278(str(EMPTY)) >= 0

def test_mod1097_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1097_times_8400_plus_shape_times_275_plus_text_times_272_plus_page_times_278
    f=fodg_file_size_mod_1097_times_8400_plus_shape_times_275_plus_text_times_272_plus_page_times_278
    assert len({f(str(EMPTY)),f(str(MINIMAL)),f(str(SHAPES))})==3

def test_mod1097_importable_from_package():
    from fodg import fodg_file_size_mod_1097_times_8400_plus_shape_times_275_plus_text_times_272_plus_page_times_278
    assert callable(fodg_file_size_mod_1097_times_8400_plus_shape_times_275_plus_text_times_272_plus_page_times_278)

def test_mod1103_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1103_times_8500_plus_shape_times_277_plus_text_times_274_plus_page_times_280
    assert isinstance(fodg_file_size_mod_1103_times_8500_plus_shape_times_277_plus_text_times_274_plus_page_times_280(str(EMPTY)), int)

def test_mod1103_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1103_times_8500_plus_shape_times_277_plus_text_times_274_plus_page_times_280
    assert fodg_file_size_mod_1103_times_8500_plus_shape_times_277_plus_text_times_274_plus_page_times_280(str(EMPTY)) >= 0

def test_mod1103_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1103_times_8500_plus_shape_times_277_plus_text_times_274_plus_page_times_280
    f=fodg_file_size_mod_1103_times_8500_plus_shape_times_277_plus_text_times_274_plus_page_times_280
    assert len({f(str(EMPTY)),f(str(MINIMAL)),f(str(SHAPES))})==3

def test_mod1103_importable_from_package():
    from fodg import fodg_file_size_mod_1103_times_8500_plus_shape_times_277_plus_text_times_274_plus_page_times_280
    assert callable(fodg_file_size_mod_1103_times_8500_plus_shape_times_277_plus_text_times_274_plus_page_times_280)
