"""Sprint 581 FODG analytics deepening tests - primes 1151, 1153."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"

def test_mod1151_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1151_times_9000_plus_shape_times_287_plus_text_times_284_plus_page_times_290
    assert fodg_file_size_mod_1151_times_9000_plus_shape_times_287_plus_text_times_284_plus_page_times_290(str(EMPTY)) == 9477290

def test_mod1151_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1151_times_9000_plus_shape_times_287_plus_text_times_284_plus_page_times_290
    assert fodg_file_size_mod_1151_times_9000_plus_shape_times_287_plus_text_times_284_plus_page_times_290(str(MINIMAL)) == 2898861

def test_mod1151_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1151_times_9000_plus_shape_times_287_plus_text_times_284_plus_page_times_290
    assert fodg_file_size_mod_1151_times_9000_plus_shape_times_287_plus_text_times_284_plus_page_times_290(str(SHAPES)) == 4294719

def test_mod1153_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1153_times_9100_plus_shape_times_289_plus_text_times_286_plus_page_times_292
    assert fodg_file_size_mod_1153_times_9100_plus_shape_times_289_plus_text_times_286_plus_page_times_292(str(EMPTY)) == 9582592

def test_mod1153_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1153_times_9100_plus_shape_times_289_plus_text_times_286_plus_page_times_292
    assert fodg_file_size_mod_1153_times_9100_plus_shape_times_289_plus_text_times_286_plus_page_times_292(str(MINIMAL)) == 2912867

def test_mod1153_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1153_times_9100_plus_shape_times_289_plus_text_times_286_plus_page_times_292
    assert fodg_file_size_mod_1153_times_9100_plus_shape_times_289_plus_text_times_286_plus_page_times_292(str(SHAPES)) == 4324231

def test_mod1151_positive():
    from fodg.fodg_analytics import fodg_file_size_mod_1151_times_9000_plus_shape_times_287_plus_text_times_284_plus_page_times_290
    assert fodg_file_size_mod_1151_times_9000_plus_shape_times_287_plus_text_times_284_plus_page_times_290(str(EMPTY)) > 0

def test_mod1153_positive():
    from fodg.fodg_analytics import fodg_file_size_mod_1153_times_9100_plus_shape_times_289_plus_text_times_286_plus_page_times_292
    assert fodg_file_size_mod_1153_times_9100_plus_shape_times_289_plus_text_times_286_plus_page_times_292(str(EMPTY)) > 0

def test_mod1151_neq_mod1153():
    from fodg.fodg_analytics import fodg_file_size_mod_1151_times_9000_plus_shape_times_287_plus_text_times_284_plus_page_times_290, fodg_file_size_mod_1153_times_9100_plus_shape_times_289_plus_text_times_286_plus_page_times_292
    assert fodg_file_size_mod_1151_times_9000_plus_shape_times_287_plus_text_times_284_plus_page_times_290(str(SHAPES)) != fodg_file_size_mod_1153_times_9100_plus_shape_times_289_plus_text_times_286_plus_page_times_292(str(SHAPES))

def test_mod1151_consistent():
    from fodg.fodg_analytics import fodg_file_size_mod_1151_times_9000_plus_shape_times_287_plus_text_times_284_plus_page_times_290
    assert fodg_file_size_mod_1151_times_9000_plus_shape_times_287_plus_text_times_284_plus_page_times_290(str(MINIMAL)) == fodg_file_size_mod_1151_times_9000_plus_shape_times_287_plus_text_times_284_plus_page_times_290(str(MINIMAL))
