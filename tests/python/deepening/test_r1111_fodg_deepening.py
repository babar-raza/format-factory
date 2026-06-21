"""Sprint 557 FODG analytics deepening tests - primes 1033, 1039."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1033_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1033_times_7400_plus_shape_times_255_plus_text_times_252_plus_page_times_258
    assert fodg_file_size_mod_1033_times_7400_plus_shape_times_255_plus_text_times_252_plus_page_times_258(str(EMPTY)) == 148258


def test_mod1033_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1033_times_7400_plus_shape_times_255_plus_text_times_252_plus_page_times_258
    assert fodg_file_size_mod_1033_times_7400_plus_shape_times_255_plus_text_times_252_plus_page_times_258(str(MINIMAL)) == 3256765


def test_mod1033_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1033_times_7400_plus_shape_times_255_plus_text_times_252_plus_page_times_258
    assert fodg_file_size_mod_1033_times_7400_plus_shape_times_255_plus_text_times_252_plus_page_times_258(str(SHAPES)) == 4404527


def test_mod1039_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1039_times_7500_plus_shape_times_257_plus_text_times_254_plus_page_times_260
    assert fodg_file_size_mod_1039_times_7500_plus_shape_times_257_plus_text_times_254_plus_page_times_260(str(EMPTY)) == 105260


def test_mod1039_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1039_times_7500_plus_shape_times_257_plus_text_times_254_plus_page_times_260
    assert fodg_file_size_mod_1039_times_7500_plus_shape_times_257_plus_text_times_254_plus_page_times_260(str(MINIMAL)) == 3255771


def test_mod1039_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1039_times_7500_plus_shape_times_257_plus_text_times_254_plus_page_times_260
    assert fodg_file_size_mod_1039_times_7500_plus_shape_times_257_plus_text_times_254_plus_page_times_260(str(SHAPES)) == 4419039


def test_mod1033_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1033_times_7400_plus_shape_times_255_plus_text_times_252_plus_page_times_258
    assert isinstance(fodg_file_size_mod_1033_times_7400_plus_shape_times_255_plus_text_times_252_plus_page_times_258(str(EMPTY)), int)


def test_mod1039_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1039_times_7500_plus_shape_times_257_plus_text_times_254_plus_page_times_260
    assert isinstance(fodg_file_size_mod_1039_times_7500_plus_shape_times_257_plus_text_times_254_plus_page_times_260(str(EMPTY)), int)


def test_mod1033_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1033_times_7400_plus_shape_times_255_plus_text_times_252_plus_page_times_258
    assert fodg_file_size_mod_1033_times_7400_plus_shape_times_255_plus_text_times_252_plus_page_times_258(str(EMPTY)) >= 0


def test_mod1039_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1039_times_7500_plus_shape_times_257_plus_text_times_254_plus_page_times_260
    assert fodg_file_size_mod_1039_times_7500_plus_shape_times_257_plus_text_times_254_plus_page_times_260(str(EMPTY)) >= 0


def test_mod1033_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1033_times_7400_plus_shape_times_255_plus_text_times_252_plus_page_times_258
    fn = fodg_file_size_mod_1033_times_7400_plus_shape_times_255_plus_text_times_252_plus_page_times_258
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1039_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1039_times_7500_plus_shape_times_257_plus_text_times_254_plus_page_times_260
    fn = fodg_file_size_mod_1039_times_7500_plus_shape_times_257_plus_text_times_254_plus_page_times_260
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1033_importable_from_package():
    from fodg import fodg_file_size_mod_1033_times_7400_plus_shape_times_255_plus_text_times_252_plus_page_times_258
    assert callable(fodg_file_size_mod_1033_times_7400_plus_shape_times_255_plus_text_times_252_plus_page_times_258)


def test_mod1039_importable_from_package():
    from fodg import fodg_file_size_mod_1039_times_7500_plus_shape_times_257_plus_text_times_254_plus_page_times_260
    assert callable(fodg_file_size_mod_1039_times_7500_plus_shape_times_257_plus_text_times_254_plus_page_times_260)
