"""Sprint 596 FODG analytics deepening tests - primes 1223, 1229."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"

def test_mod1223_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1223_times_10000_plus_shape_times_307_plus_text_times_304_plus_page_times_310
    assert fodg_file_size_mod_1223_times_10000_plus_shape_times_307_plus_text_times_304_plus_page_times_310(str(EMPTY)) == 10530310

def test_mod1223_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1223_times_10000_plus_shape_times_307_plus_text_times_304_plus_page_times_310
    assert fodg_file_size_mod_1223_times_10000_plus_shape_times_307_plus_text_times_304_plus_page_times_310(str(MINIMAL)) == 2500921

def test_mod1223_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1223_times_10000_plus_shape_times_307_plus_text_times_304_plus_page_times_310
    assert fodg_file_size_mod_1223_times_10000_plus_shape_times_307_plus_text_times_304_plus_page_times_310(str(SHAPES)) == 4051839

def test_mod1229_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1229_times_10100_plus_shape_times_309_plus_text_times_306_plus_page_times_312
    assert fodg_file_size_mod_1229_times_10100_plus_shape_times_309_plus_text_times_306_plus_page_times_312(str(EMPTY)) == 10635612

def test_mod1229_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1229_times_10100_plus_shape_times_309_plus_text_times_306_plus_page_times_312
    assert fodg_file_size_mod_1229_times_10100_plus_shape_times_309_plus_text_times_306_plus_page_times_312(str(MINIMAL)) == 2465327

def test_mod1229_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1229_times_10100_plus_shape_times_309_plus_text_times_306_plus_page_times_312
    assert fodg_file_size_mod_1229_times_10100_plus_shape_times_309_plus_text_times_306_plus_page_times_312(str(SHAPES)) == 4031751

def test_mod1223_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1223_times_10000_plus_shape_times_307_plus_text_times_304_plus_page_times_310
    assert isinstance(fodg_file_size_mod_1223_times_10000_plus_shape_times_307_plus_text_times_304_plus_page_times_310(str(EMPTY)), int)

def test_mod1223_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1223_times_10000_plus_shape_times_307_plus_text_times_304_plus_page_times_310
    assert fodg_file_size_mod_1223_times_10000_plus_shape_times_307_plus_text_times_304_plus_page_times_310(str(EMPTY)) >= 0

def test_mod1223_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1223_times_10000_plus_shape_times_307_plus_text_times_304_plus_page_times_310
    fn2 = fodg_file_size_mod_1223_times_10000_plus_shape_times_307_plus_text_times_304_plus_page_times_310
    results = {fn2(str(EMPTY)), fn2(str(MINIMAL)), fn2(str(SHAPES))}
    assert len(results) == 3

def test_mod1223_importable_from_package():
    from fodg import fodg_file_size_mod_1223_times_10000_plus_shape_times_307_plus_text_times_304_plus_page_times_310
    assert callable(fodg_file_size_mod_1223_times_10000_plus_shape_times_307_plus_text_times_304_plus_page_times_310)

def test_mod1229_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1229_times_10100_plus_shape_times_309_plus_text_times_306_plus_page_times_312
    assert isinstance(fodg_file_size_mod_1229_times_10100_plus_shape_times_309_plus_text_times_306_plus_page_times_312(str(EMPTY)), int)

def test_mod1229_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1229_times_10100_plus_shape_times_309_plus_text_times_306_plus_page_times_312
    assert fodg_file_size_mod_1229_times_10100_plus_shape_times_309_plus_text_times_306_plus_page_times_312(str(EMPTY)) >= 0

def test_mod1229_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1229_times_10100_plus_shape_times_309_plus_text_times_306_plus_page_times_312
    fn2 = fodg_file_size_mod_1229_times_10100_plus_shape_times_309_plus_text_times_306_plus_page_times_312
    results = {fn2(str(EMPTY)), fn2(str(MINIMAL)), fn2(str(SHAPES))}
    assert len(results) == 3

def test_mod1229_importable_from_package():
    from fodg import fodg_file_size_mod_1229_times_10100_plus_shape_times_309_plus_text_times_306_plus_page_times_312
    assert callable(fodg_file_size_mod_1229_times_10100_plus_shape_times_309_plus_text_times_306_plus_page_times_312)
