"""Sprint 617 FODG analytics deepening tests - primes 1307, 1319."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1307_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1307_times_11400_plus_shape_times_335_plus_text_times_332_plus_page_times_338
    assert fodg_file_size_mod_1307_times_11400_plus_shape_times_335_plus_text_times_332_plus_page_times_338(str(EMPTY)) == 12004538


def test_mod1307_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1307_times_11400_plus_shape_times_335_plus_text_times_332_plus_page_times_338
    assert fodg_file_size_mod_1307_times_11400_plus_shape_times_335_plus_text_times_332_plus_page_times_338(str(MINIMAL)) == 1893405


def test_mod1307_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1307_times_11400_plus_shape_times_335_plus_text_times_332_plus_page_times_338
    assert fodg_file_size_mod_1307_times_11400_plus_shape_times_335_plus_text_times_332_plus_page_times_338(str(SHAPES)) == 3661407


def test_mod1319_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1319_times_11500_plus_shape_times_337_plus_text_times_334_plus_page_times_340
    assert fodg_file_size_mod_1319_times_11500_plus_shape_times_337_plus_text_times_334_plus_page_times_340(str(EMPTY)) == 12109840


def test_mod1319_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1319_times_11500_plus_shape_times_337_plus_text_times_334_plus_page_times_340
    assert fodg_file_size_mod_1319_times_11500_plus_shape_times_337_plus_text_times_334_plus_page_times_340(str(MINIMAL)) == 1772011


def test_mod1319_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1319_times_11500_plus_shape_times_337_plus_text_times_334_plus_page_times_340
    assert fodg_file_size_mod_1319_times_11500_plus_shape_times_337_plus_text_times_334_plus_page_times_340(str(SHAPES)) == 3555519


def test_mod1307_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1307_times_11400_plus_shape_times_335_plus_text_times_332_plus_page_times_338
    assert isinstance(fodg_file_size_mod_1307_times_11400_plus_shape_times_335_plus_text_times_332_plus_page_times_338(str(EMPTY)), int)


def test_mod1319_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1319_times_11500_plus_shape_times_337_plus_text_times_334_plus_page_times_340
    assert isinstance(fodg_file_size_mod_1319_times_11500_plus_shape_times_337_plus_text_times_334_plus_page_times_340(str(EMPTY)), int)


def test_mod1307_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1307_times_11400_plus_shape_times_335_plus_text_times_332_plus_page_times_338
    assert fodg_file_size_mod_1307_times_11400_plus_shape_times_335_plus_text_times_332_plus_page_times_338(str(EMPTY)) >= 0


def test_mod1319_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1319_times_11500_plus_shape_times_337_plus_text_times_334_plus_page_times_340
    assert fodg_file_size_mod_1319_times_11500_plus_shape_times_337_plus_text_times_334_plus_page_times_340(str(EMPTY)) >= 0


def test_mod1307_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1307_times_11400_plus_shape_times_335_plus_text_times_332_plus_page_times_338
    fn = fodg_file_size_mod_1307_times_11400_plus_shape_times_335_plus_text_times_332_plus_page_times_338
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1319_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1319_times_11500_plus_shape_times_337_plus_text_times_334_plus_page_times_340
    fn = fodg_file_size_mod_1319_times_11500_plus_shape_times_337_plus_text_times_334_plus_page_times_340
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1307_importable_from_package():
    from fodg import fodg_file_size_mod_1307_times_11400_plus_shape_times_335_plus_text_times_332_plus_page_times_338
    assert callable(fodg_file_size_mod_1307_times_11400_plus_shape_times_335_plus_text_times_332_plus_page_times_338)


def test_mod1319_importable_from_package():
    from fodg import fodg_file_size_mod_1319_times_11500_plus_shape_times_337_plus_text_times_334_plus_page_times_340
    assert callable(fodg_file_size_mod_1319_times_11500_plus_shape_times_337_plus_text_times_334_plus_page_times_340)
