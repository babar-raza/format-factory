"""Sprint 605 FODG analytics deepening tests - primes 1277, 1279."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"

def test_mod1277_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1277_times_10600_plus_shape_times_319_plus_text_times_316_plus_page_times_322
    assert fodg_file_size_mod_1277_times_10600_plus_shape_times_319_plus_text_times_316_plus_page_times_322(str(EMPTY)) == 11162122

def test_mod1277_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1277_times_10600_plus_shape_times_319_plus_text_times_316_plus_page_times_322
    assert fodg_file_size_mod_1277_times_10600_plus_shape_times_319_plus_text_times_316_plus_page_times_322(str(MINIMAL)) == 2078557

def test_mod1277_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1277_times_10600_plus_shape_times_319_plus_text_times_316_plus_page_times_322
    assert fodg_file_size_mod_1277_times_10600_plus_shape_times_319_plus_text_times_316_plus_page_times_322(str(SHAPES)) == 3722511

def test_mod1279_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1279_times_10700_plus_shape_times_321_plus_text_times_318_plus_page_times_324
    assert fodg_file_size_mod_1279_times_10700_plus_shape_times_321_plus_text_times_318_plus_page_times_324(str(EMPTY)) == 11267424

def test_mod1279_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1279_times_10700_plus_shape_times_321_plus_text_times_318_plus_page_times_324
    assert fodg_file_size_mod_1279_times_10700_plus_shape_times_321_plus_text_times_318_plus_page_times_324(str(MINIMAL)) == 2076763

def test_mod1279_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1279_times_10700_plus_shape_times_321_plus_text_times_318_plus_page_times_324
    assert fodg_file_size_mod_1279_times_10700_plus_shape_times_321_plus_text_times_318_plus_page_times_324(str(SHAPES)) == 3736223

def test_mod1277_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1277_times_10600_plus_shape_times_319_plus_text_times_316_plus_page_times_322
    assert isinstance(fodg_file_size_mod_1277_times_10600_plus_shape_times_319_plus_text_times_316_plus_page_times_322(str(EMPTY)), int)

def test_mod1277_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1277_times_10600_plus_shape_times_319_plus_text_times_316_plus_page_times_322
    assert fodg_file_size_mod_1277_times_10600_plus_shape_times_319_plus_text_times_316_plus_page_times_322(str(EMPTY)) >= 0

def test_mod1277_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1277_times_10600_plus_shape_times_319_plus_text_times_316_plus_page_times_322
    fn2 = fodg_file_size_mod_1277_times_10600_plus_shape_times_319_plus_text_times_316_plus_page_times_322
    results = {fn2(str(EMPTY)), fn2(str(MINIMAL)), fn2(str(SHAPES))}
    assert len(results) == 3

def test_mod1277_importable_from_package():
    from fodg import fodg_file_size_mod_1277_times_10600_plus_shape_times_319_plus_text_times_316_plus_page_times_322
    assert callable(fodg_file_size_mod_1277_times_10600_plus_shape_times_319_plus_text_times_316_plus_page_times_322)

def test_mod1279_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1279_times_10700_plus_shape_times_321_plus_text_times_318_plus_page_times_324
    assert isinstance(fodg_file_size_mod_1279_times_10700_plus_shape_times_321_plus_text_times_318_plus_page_times_324(str(EMPTY)), int)

def test_mod1279_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1279_times_10700_plus_shape_times_321_plus_text_times_318_plus_page_times_324
    assert fodg_file_size_mod_1279_times_10700_plus_shape_times_321_plus_text_times_318_plus_page_times_324(str(EMPTY)) >= 0

def test_mod1279_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1279_times_10700_plus_shape_times_321_plus_text_times_318_plus_page_times_324
    fn2 = fodg_file_size_mod_1279_times_10700_plus_shape_times_321_plus_text_times_318_plus_page_times_324
    results = {fn2(str(EMPTY)), fn2(str(MINIMAL)), fn2(str(SHAPES))}
    assert len(results) == 3

def test_mod1279_importable_from_package():
    from fodg import fodg_file_size_mod_1279_times_10700_plus_shape_times_321_plus_text_times_318_plus_page_times_324
    assert callable(fodg_file_size_mod_1279_times_10700_plus_shape_times_321_plus_text_times_318_plus_page_times_324)
