"""Sprint 611 FODG analytics deepening tests - primes 1291, 1297."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1291_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1291_times_11000_plus_shape_times_327_plus_text_times_324_plus_page_times_330
    assert fodg_file_size_mod_1291_times_11000_plus_shape_times_327_plus_text_times_324_plus_page_times_330(str(EMPTY)) == 11583330


def test_mod1291_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1291_times_11000_plus_shape_times_327_plus_text_times_324_plus_page_times_330
    assert fodg_file_size_mod_1291_times_11000_plus_shape_times_327_plus_text_times_324_plus_page_times_330(str(MINIMAL)) == 2002981


def test_mod1291_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1291_times_11000_plus_shape_times_327_plus_text_times_324_plus_page_times_330
    assert fodg_file_size_mod_1291_times_11000_plus_shape_times_327_plus_text_times_324_plus_page_times_330(str(SHAPES)) == 3708959


def test_mod1297_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1297_times_11100_plus_shape_times_329_plus_text_times_326_plus_page_times_332
    assert fodg_file_size_mod_1297_times_11100_plus_shape_times_329_plus_text_times_326_plus_page_times_332(str(EMPTY)) == 11688632


def test_mod1297_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1297_times_11100_plus_shape_times_329_plus_text_times_326_plus_page_times_332
    assert fodg_file_size_mod_1297_times_11100_plus_shape_times_329_plus_text_times_326_plus_page_times_332(str(MINIMAL)) == 1954587


def test_mod1297_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1297_times_11100_plus_shape_times_329_plus_text_times_326_plus_page_times_332
    assert fodg_file_size_mod_1297_times_11100_plus_shape_times_329_plus_text_times_326_plus_page_times_332(str(SHAPES)) == 3676071


def test_mod1291_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1291_times_11000_plus_shape_times_327_plus_text_times_324_plus_page_times_330
    assert isinstance(fodg_file_size_mod_1291_times_11000_plus_shape_times_327_plus_text_times_324_plus_page_times_330(str(EMPTY)), int)


def test_mod1297_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1297_times_11100_plus_shape_times_329_plus_text_times_326_plus_page_times_332
    assert isinstance(fodg_file_size_mod_1297_times_11100_plus_shape_times_329_plus_text_times_326_plus_page_times_332(str(EMPTY)), int)


def test_mod1291_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1291_times_11000_plus_shape_times_327_plus_text_times_324_plus_page_times_330
    assert fodg_file_size_mod_1291_times_11000_plus_shape_times_327_plus_text_times_324_plus_page_times_330(str(EMPTY)) >= 0


def test_mod1297_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1297_times_11100_plus_shape_times_329_plus_text_times_326_plus_page_times_332
    assert fodg_file_size_mod_1297_times_11100_plus_shape_times_329_plus_text_times_326_plus_page_times_332(str(EMPTY)) >= 0


def test_mod1291_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1291_times_11000_plus_shape_times_327_plus_text_times_324_plus_page_times_330
    fn = fodg_file_size_mod_1291_times_11000_plus_shape_times_327_plus_text_times_324_plus_page_times_330
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1297_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1297_times_11100_plus_shape_times_329_plus_text_times_326_plus_page_times_332
    fn = fodg_file_size_mod_1297_times_11100_plus_shape_times_329_plus_text_times_326_plus_page_times_332
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1291_importable_from_package():
    from fodg import fodg_file_size_mod_1291_times_11000_plus_shape_times_327_plus_text_times_324_plus_page_times_330
    assert callable(fodg_file_size_mod_1291_times_11000_plus_shape_times_327_plus_text_times_324_plus_page_times_330)


def test_mod1297_importable_from_package():
    from fodg import fodg_file_size_mod_1297_times_11100_plus_shape_times_329_plus_text_times_326_plus_page_times_332
    assert callable(fodg_file_size_mod_1297_times_11100_plus_shape_times_329_plus_text_times_326_plus_page_times_332)
