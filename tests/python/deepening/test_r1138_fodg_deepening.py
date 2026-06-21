"""Sprint 584 FODG analytics deepening tests - primes 1163, 1171."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"

def test_mod1163_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1163_times_9200_plus_shape_times_291_plus_text_times_288_plus_page_times_294
    assert fodg_file_size_mod_1163_times_9200_plus_shape_times_291_plus_text_times_288_plus_page_times_294(str(EMPTY)) == 9687894

def test_mod1163_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1163_times_9200_plus_shape_times_291_plus_text_times_288_plus_page_times_294
    assert fodg_file_size_mod_1163_times_9200_plus_shape_times_291_plus_text_times_288_plus_page_times_294(str(MINIMAL)) == 2852873

def test_mod1163_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1163_times_9200_plus_shape_times_291_plus_text_times_288_plus_page_times_294
    assert fodg_file_size_mod_1163_times_9200_plus_shape_times_291_plus_text_times_288_plus_page_times_294(str(SHAPES)) == 4279743

def test_mod1171_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1171_times_9300_plus_shape_times_293_plus_text_times_290_plus_page_times_296
    assert fodg_file_size_mod_1171_times_9300_plus_shape_times_293_plus_text_times_290_plus_page_times_296(str(EMPTY)) == 9793196

def test_mod1171_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1171_times_9300_plus_shape_times_293_plus_text_times_290_plus_page_times_296
    assert fodg_file_size_mod_1171_times_9300_plus_shape_times_293_plus_text_times_290_plus_page_times_296(str(MINIMAL)) == 2809479

def test_mod1171_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1171_times_9300_plus_shape_times_293_plus_text_times_290_plus_page_times_296
    assert fodg_file_size_mod_1171_times_9300_plus_shape_times_293_plus_text_times_290_plus_page_times_296(str(SHAPES)) == 4251855

def test_mod1163_positive():
    from fodg.fodg_analytics import fodg_file_size_mod_1163_times_9200_plus_shape_times_291_plus_text_times_288_plus_page_times_294
    assert fodg_file_size_mod_1163_times_9200_plus_shape_times_291_plus_text_times_288_plus_page_times_294(str(EMPTY)) > 0

def test_mod1171_positive():
    from fodg.fodg_analytics import fodg_file_size_mod_1171_times_9300_plus_shape_times_293_plus_text_times_290_plus_page_times_296
    assert fodg_file_size_mod_1171_times_9300_plus_shape_times_293_plus_text_times_290_plus_page_times_296(str(EMPTY)) > 0

def test_mod1163_neq_mod1171():
    from fodg.fodg_analytics import fodg_file_size_mod_1163_times_9200_plus_shape_times_291_plus_text_times_288_plus_page_times_294, fodg_file_size_mod_1171_times_9300_plus_shape_times_293_plus_text_times_290_plus_page_times_296
    assert fodg_file_size_mod_1163_times_9200_plus_shape_times_291_plus_text_times_288_plus_page_times_294(str(SHAPES)) != fodg_file_size_mod_1171_times_9300_plus_shape_times_293_plus_text_times_290_plus_page_times_296(str(SHAPES))

def test_mod1163_consistent():
    from fodg.fodg_analytics import fodg_file_size_mod_1163_times_9200_plus_shape_times_291_plus_text_times_288_plus_page_times_294
    assert fodg_file_size_mod_1163_times_9200_plus_shape_times_291_plus_text_times_288_plus_page_times_294(str(MINIMAL)) == fodg_file_size_mod_1163_times_9200_plus_shape_times_291_plus_text_times_288_plus_page_times_294(str(MINIMAL))
