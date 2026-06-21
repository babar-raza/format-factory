"""Sprint 590 FODG analytics deepening tests - primes 1193, 1201."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"

def test_mod1193_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1193_times_9600_plus_shape_times_299_plus_text_times_296_plus_page_times_302
    assert fodg_file_size_mod_1193_times_9600_plus_shape_times_299_plus_text_times_296_plus_page_times_302(str(EMPTY)) == 10109102

def test_mod1193_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1193_times_9600_plus_shape_times_299_plus_text_times_296_plus_page_times_302
    assert fodg_file_size_mod_1193_times_9600_plus_shape_times_299_plus_text_times_296_plus_page_times_302(str(MINIMAL)) == 2688897

def test_mod1193_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1193_times_9600_plus_shape_times_299_plus_text_times_296_plus_page_times_302
    assert fodg_file_size_mod_1193_times_9600_plus_shape_times_299_plus_text_times_296_plus_page_times_302(str(SHAPES)) == 4177791

def test_mod1201_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1201_times_9700_plus_shape_times_301_plus_text_times_298_plus_page_times_304
    assert fodg_file_size_mod_1201_times_9700_plus_shape_times_301_plus_text_times_298_plus_page_times_304(str(EMPTY)) == 10214404

def test_mod1201_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1201_times_9700_plus_shape_times_301_plus_text_times_298_plus_page_times_304
    assert fodg_file_size_mod_1201_times_9700_plus_shape_times_301_plus_text_times_298_plus_page_times_304(str(MINIMAL)) == 2639303

def test_mod1201_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1201_times_9700_plus_shape_times_301_plus_text_times_298_plus_page_times_304
    assert fodg_file_size_mod_1201_times_9700_plus_shape_times_301_plus_text_times_298_plus_page_times_304(str(SHAPES)) == 4143703

def test_mod1193_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1193_times_9600_plus_shape_times_299_plus_text_times_296_plus_page_times_302
    assert isinstance(fodg_file_size_mod_1193_times_9600_plus_shape_times_299_plus_text_times_296_plus_page_times_302(str(EMPTY)), int)

def test_mod1193_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1193_times_9600_plus_shape_times_299_plus_text_times_296_plus_page_times_302
    assert fodg_file_size_mod_1193_times_9600_plus_shape_times_299_plus_text_times_296_plus_page_times_302(str(EMPTY)) >= 0

def test_mod1193_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1193_times_9600_plus_shape_times_299_plus_text_times_296_plus_page_times_302
    fn2 = fodg_file_size_mod_1193_times_9600_plus_shape_times_299_plus_text_times_296_plus_page_times_302
    results = {fn2(str(EMPTY)), fn2(str(MINIMAL)), fn2(str(SHAPES))}
    assert len(results) == 3

def test_mod1193_importable_from_package():
    from fodg import fodg_file_size_mod_1193_times_9600_plus_shape_times_299_plus_text_times_296_plus_page_times_302
    assert callable(fodg_file_size_mod_1193_times_9600_plus_shape_times_299_plus_text_times_296_plus_page_times_302)

def test_mod1201_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1201_times_9700_plus_shape_times_301_plus_text_times_298_plus_page_times_304
    assert isinstance(fodg_file_size_mod_1201_times_9700_plus_shape_times_301_plus_text_times_298_plus_page_times_304(str(EMPTY)), int)

def test_mod1201_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1201_times_9700_plus_shape_times_301_plus_text_times_298_plus_page_times_304
    assert fodg_file_size_mod_1201_times_9700_plus_shape_times_301_plus_text_times_298_plus_page_times_304(str(EMPTY)) >= 0

def test_mod1201_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1201_times_9700_plus_shape_times_301_plus_text_times_298_plus_page_times_304
    fn2 = fodg_file_size_mod_1201_times_9700_plus_shape_times_301_plus_text_times_298_plus_page_times_304
    results = {fn2(str(EMPTY)), fn2(str(MINIMAL)), fn2(str(SHAPES))}
    assert len(results) == 3

def test_mod1201_importable_from_package():
    from fodg import fodg_file_size_mod_1201_times_9700_plus_shape_times_301_plus_text_times_298_plus_page_times_304
    assert callable(fodg_file_size_mod_1201_times_9700_plus_shape_times_301_plus_text_times_298_plus_page_times_304)
