"""Sprint 569 FODG analytics deepening tests - primes 1091, 1093."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"

def test_mod1091_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1091_times_8200_plus_shape_times_271_plus_text_times_268_plus_page_times_274
    assert fodg_file_size_mod_1091_times_8200_plus_shape_times_271_plus_text_times_268_plus_page_times_274(str(EMPTY)) == 8634874

def test_mod1091_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1091_times_8200_plus_shape_times_271_plus_text_times_268_plus_page_times_274
    assert fodg_file_size_mod_1091_times_8200_plus_shape_times_271_plus_text_times_268_plus_page_times_274(str(MINIMAL)) == 3133213

def test_mod1091_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1091_times_8200_plus_shape_times_271_plus_text_times_268_plus_page_times_274
    assert fodg_file_size_mod_1091_times_8200_plus_shape_times_271_plus_text_times_268_plus_page_times_274(str(SHAPES)) == 4405023

def test_mod1093_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1093_times_8300_plus_shape_times_273_plus_text_times_270_plus_page_times_276
    assert fodg_file_size_mod_1093_times_8300_plus_shape_times_273_plus_text_times_270_plus_page_times_276(str(EMPTY)) == 8740176

def test_mod1093_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1093_times_8300_plus_shape_times_273_plus_text_times_270_plus_page_times_276
    assert fodg_file_size_mod_1093_times_8300_plus_shape_times_273_plus_text_times_270_plus_page_times_276(str(MINIMAL)) == 3154819

def test_mod1093_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1093_times_8300_plus_shape_times_273_plus_text_times_270_plus_page_times_276
    assert fodg_file_size_mod_1093_times_8300_plus_shape_times_273_plus_text_times_270_plus_page_times_276(str(SHAPES)) == 4442135

def test_mod1091_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1091_times_8200_plus_shape_times_271_plus_text_times_268_plus_page_times_274
    assert isinstance(fodg_file_size_mod_1091_times_8200_plus_shape_times_271_plus_text_times_268_plus_page_times_274(str(EMPTY)), int)

def test_mod1091_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1091_times_8200_plus_shape_times_271_plus_text_times_268_plus_page_times_274
    assert fodg_file_size_mod_1091_times_8200_plus_shape_times_271_plus_text_times_268_plus_page_times_274(str(EMPTY)) >= 0

def test_mod1091_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1091_times_8200_plus_shape_times_271_plus_text_times_268_plus_page_times_274
    fn = fodg_file_size_mod_1091_times_8200_plus_shape_times_271_plus_text_times_268_plus_page_times_274
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3

def test_mod1091_importable_from_package():
    from fodg import fodg_file_size_mod_1091_times_8200_plus_shape_times_271_plus_text_times_268_plus_page_times_274
    assert callable(fodg_file_size_mod_1091_times_8200_plus_shape_times_271_plus_text_times_268_plus_page_times_274)

def test_mod1093_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1093_times_8300_plus_shape_times_273_plus_text_times_270_plus_page_times_276
    assert isinstance(fodg_file_size_mod_1093_times_8300_plus_shape_times_273_plus_text_times_270_plus_page_times_276(str(EMPTY)), int)

def test_mod1093_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1093_times_8300_plus_shape_times_273_plus_text_times_270_plus_page_times_276
    assert fodg_file_size_mod_1093_times_8300_plus_shape_times_273_plus_text_times_270_plus_page_times_276(str(EMPTY)) >= 0

def test_mod1093_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1093_times_8300_plus_shape_times_273_plus_text_times_270_plus_page_times_276
    fn = fodg_file_size_mod_1093_times_8300_plus_shape_times_273_plus_text_times_270_plus_page_times_276
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3

def test_mod1093_importable_from_package():
    from fodg import fodg_file_size_mod_1093_times_8300_plus_shape_times_273_plus_text_times_270_plus_page_times_276
    assert callable(fodg_file_size_mod_1093_times_8300_plus_shape_times_273_plus_text_times_270_plus_page_times_276)
