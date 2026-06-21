"""Sprint 593 FODG analytics deepening tests - primes 1213, 1217."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"

def test_mod1213_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1213_times_9800_plus_shape_times_303_plus_text_times_300_plus_page_times_306
    assert fodg_file_size_mod_1213_times_9800_plus_shape_times_303_plus_text_times_300_plus_page_times_306(str(EMPTY)) == 10319706

def test_mod1213_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1213_times_9800_plus_shape_times_303_plus_text_times_300_plus_page_times_306
    assert fodg_file_size_mod_1213_times_9800_plus_shape_times_303_plus_text_times_300_plus_page_times_306(str(MINIMAL)) == 2548909

def test_mod1213_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1213_times_9800_plus_shape_times_303_plus_text_times_300_plus_page_times_306
    assert fodg_file_size_mod_1213_times_9800_plus_shape_times_303_plus_text_times_300_plus_page_times_306(str(SHAPES)) == 4068815

def test_mod1217_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1217_times_9900_plus_shape_times_305_plus_text_times_302_plus_page_times_308
    assert fodg_file_size_mod_1217_times_9900_plus_shape_times_305_plus_text_times_302_plus_page_times_308(str(EMPTY)) == 10425008

def test_mod1217_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1217_times_9900_plus_shape_times_305_plus_text_times_302_plus_page_times_308
    assert fodg_file_size_mod_1217_times_9900_plus_shape_times_305_plus_text_times_302_plus_page_times_308(str(MINIMAL)) == 2535315

def test_mod1217_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1217_times_9900_plus_shape_times_305_plus_text_times_302_plus_page_times_308
    assert fodg_file_size_mod_1217_times_9900_plus_shape_times_305_plus_text_times_302_plus_page_times_308(str(SHAPES)) == 4070727

def test_mod1213_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1213_times_9800_plus_shape_times_303_plus_text_times_300_plus_page_times_306
    assert isinstance(fodg_file_size_mod_1213_times_9800_plus_shape_times_303_plus_text_times_300_plus_page_times_306(str(EMPTY)), int)

def test_mod1213_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1213_times_9800_plus_shape_times_303_plus_text_times_300_plus_page_times_306
    assert fodg_file_size_mod_1213_times_9800_plus_shape_times_303_plus_text_times_300_plus_page_times_306(str(EMPTY)) >= 0

def test_mod1213_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1213_times_9800_plus_shape_times_303_plus_text_times_300_plus_page_times_306
    fn2 = fodg_file_size_mod_1213_times_9800_plus_shape_times_303_plus_text_times_300_plus_page_times_306
    results = {fn2(str(EMPTY)), fn2(str(MINIMAL)), fn2(str(SHAPES))}
    assert len(results) == 3

def test_mod1213_importable_from_package():
    from fodg import fodg_file_size_mod_1213_times_9800_plus_shape_times_303_plus_text_times_300_plus_page_times_306
    assert callable(fodg_file_size_mod_1213_times_9800_plus_shape_times_303_plus_text_times_300_plus_page_times_306)

def test_mod1217_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1217_times_9900_plus_shape_times_305_plus_text_times_302_plus_page_times_308
    assert isinstance(fodg_file_size_mod_1217_times_9900_plus_shape_times_305_plus_text_times_302_plus_page_times_308(str(EMPTY)), int)

def test_mod1217_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1217_times_9900_plus_shape_times_305_plus_text_times_302_plus_page_times_308
    assert fodg_file_size_mod_1217_times_9900_plus_shape_times_305_plus_text_times_302_plus_page_times_308(str(EMPTY)) >= 0

def test_mod1217_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1217_times_9900_plus_shape_times_305_plus_text_times_302_plus_page_times_308
    fn2 = fodg_file_size_mod_1217_times_9900_plus_shape_times_305_plus_text_times_302_plus_page_times_308
    results = {fn2(str(EMPTY)), fn2(str(MINIMAL)), fn2(str(SHAPES))}
    assert len(results) == 3

def test_mod1217_importable_from_package():
    from fodg import fodg_file_size_mod_1217_times_9900_plus_shape_times_305_plus_text_times_302_plus_page_times_308
    assert callable(fodg_file_size_mod_1217_times_9900_plus_shape_times_305_plus_text_times_302_plus_page_times_308)
