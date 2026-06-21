"""Sprint 599 FODG analytics deepening tests - primes 1231, 1237."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"

def test_mod1231_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1231_times_10200_plus_shape_times_311_plus_text_times_308_plus_page_times_314
    assert fodg_file_size_mod_1231_times_10200_plus_shape_times_311_plus_text_times_308_plus_page_times_314(str(EMPTY)) == 10740914

def test_mod1231_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1231_times_10200_plus_shape_times_311_plus_text_times_308_plus_page_times_314
    assert fodg_file_size_mod_1231_times_10200_plus_shape_times_311_plus_text_times_308_plus_page_times_314(str(MINIMAL)) == 2469333

def test_mod1231_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1231_times_10200_plus_shape_times_311_plus_text_times_308_plus_page_times_314
    assert fodg_file_size_mod_1231_times_10200_plus_shape_times_311_plus_text_times_308_plus_page_times_314(str(SHAPES)) == 4051263

def test_mod1237_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1237_times_10300_plus_shape_times_313_plus_text_times_310_plus_page_times_316
    assert fodg_file_size_mod_1237_times_10300_plus_shape_times_313_plus_text_times_310_plus_page_times_316(str(EMPTY)) == 10846216

def test_mod1237_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1237_times_10300_plus_shape_times_313_plus_text_times_310_plus_page_times_316
    assert fodg_file_size_mod_1237_times_10300_plus_shape_times_313_plus_text_times_310_plus_page_times_316(str(MINIMAL)) == 2431739

def test_mod1237_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1237_times_10300_plus_shape_times_313_plus_text_times_310_plus_page_times_316
    assert fodg_file_size_mod_1237_times_10300_plus_shape_times_313_plus_text_times_310_plus_page_times_316(str(SHAPES)) == 4029175

def test_mod1231_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1231_times_10200_plus_shape_times_311_plus_text_times_308_plus_page_times_314
    assert isinstance(fodg_file_size_mod_1231_times_10200_plus_shape_times_311_plus_text_times_308_plus_page_times_314(str(EMPTY)), int)

def test_mod1231_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1231_times_10200_plus_shape_times_311_plus_text_times_308_plus_page_times_314
    assert fodg_file_size_mod_1231_times_10200_plus_shape_times_311_plus_text_times_308_plus_page_times_314(str(EMPTY)) >= 0

def test_mod1231_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1231_times_10200_plus_shape_times_311_plus_text_times_308_plus_page_times_314
    fn2 = fodg_file_size_mod_1231_times_10200_plus_shape_times_311_plus_text_times_308_plus_page_times_314
    results = {fn2(str(EMPTY)), fn2(str(MINIMAL)), fn2(str(SHAPES))}
    assert len(results) == 3

def test_mod1231_importable_from_package():
    from fodg import fodg_file_size_mod_1231_times_10200_plus_shape_times_311_plus_text_times_308_plus_page_times_314
    assert callable(fodg_file_size_mod_1231_times_10200_plus_shape_times_311_plus_text_times_308_plus_page_times_314)

def test_mod1237_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1237_times_10300_plus_shape_times_313_plus_text_times_310_plus_page_times_316
    assert isinstance(fodg_file_size_mod_1237_times_10300_plus_shape_times_313_plus_text_times_310_plus_page_times_316(str(EMPTY)), int)

def test_mod1237_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1237_times_10300_plus_shape_times_313_plus_text_times_310_plus_page_times_316
    assert fodg_file_size_mod_1237_times_10300_plus_shape_times_313_plus_text_times_310_plus_page_times_316(str(EMPTY)) >= 0

def test_mod1237_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1237_times_10300_plus_shape_times_313_plus_text_times_310_plus_page_times_316
    fn2 = fodg_file_size_mod_1237_times_10300_plus_shape_times_313_plus_text_times_310_plus_page_times_316
    results = {fn2(str(EMPTY)), fn2(str(MINIMAL)), fn2(str(SHAPES))}
    assert len(results) == 3

def test_mod1237_importable_from_package():
    from fodg import fodg_file_size_mod_1237_times_10300_plus_shape_times_313_plus_text_times_310_plus_page_times_316
    assert callable(fodg_file_size_mod_1237_times_10300_plus_shape_times_313_plus_text_times_310_plus_page_times_316)
