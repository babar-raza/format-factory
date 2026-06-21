"""Sprint 644 FODG analytics deepening tests - primes 1459, 1471."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1459_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1459_times_13200_plus_shape_times_371_plus_text_times_368_plus_page_times_374
    assert fodg_file_size_mod_1459_times_13200_plus_shape_times_371_plus_text_times_368_plus_page_times_374(str(EMPTY)) == 13899974


def test_mod1459_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1459_times_13200_plus_shape_times_371_plus_text_times_368_plus_page_times_374
    assert fodg_file_size_mod_1459_times_13200_plus_shape_times_371_plus_text_times_368_plus_page_times_374(str(MINIMAL)) == 185913


def test_mod1459_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1459_times_13200_plus_shape_times_371_plus_text_times_368_plus_page_times_374
    assert fodg_file_size_mod_1459_times_13200_plus_shape_times_371_plus_text_times_368_plus_page_times_374(str(SHAPES)) == 2233023


def test_mod1471_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1471_times_13300_plus_shape_times_373_plus_text_times_370_plus_page_times_376
    assert fodg_file_size_mod_1471_times_13300_plus_shape_times_373_plus_text_times_370_plus_page_times_376(str(EMPTY)) == 14005276


def test_mod1471_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1471_times_13300_plus_shape_times_373_plus_text_times_370_plus_page_times_376
    assert fodg_file_size_mod_1471_times_13300_plus_shape_times_373_plus_text_times_370_plus_page_times_376(str(MINIMAL)) == 27719


def test_mod1471_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1471_times_13300_plus_shape_times_373_plus_text_times_370_plus_page_times_376
    assert fodg_file_size_mod_1471_times_13300_plus_shape_times_373_plus_text_times_370_plus_page_times_376(str(SHAPES)) == 2090335


def test_mod1459_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1459_times_13200_plus_shape_times_371_plus_text_times_368_plus_page_times_374
    assert isinstance(fodg_file_size_mod_1459_times_13200_plus_shape_times_371_plus_text_times_368_plus_page_times_374(str(EMPTY)), int)


def test_mod1471_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1471_times_13300_plus_shape_times_373_plus_text_times_370_plus_page_times_376
    assert isinstance(fodg_file_size_mod_1471_times_13300_plus_shape_times_373_plus_text_times_370_plus_page_times_376(str(EMPTY)), int)


def test_mod1459_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1459_times_13200_plus_shape_times_371_plus_text_times_368_plus_page_times_374
    assert fodg_file_size_mod_1459_times_13200_plus_shape_times_371_plus_text_times_368_plus_page_times_374(str(EMPTY)) >= 0


def test_mod1471_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1471_times_13300_plus_shape_times_373_plus_text_times_370_plus_page_times_376
    assert fodg_file_size_mod_1471_times_13300_plus_shape_times_373_plus_text_times_370_plus_page_times_376(str(EMPTY)) >= 0


def test_mod1459_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1459_times_13200_plus_shape_times_371_plus_text_times_368_plus_page_times_374
    fn = fodg_file_size_mod_1459_times_13200_plus_shape_times_371_plus_text_times_368_plus_page_times_374
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1471_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1471_times_13300_plus_shape_times_373_plus_text_times_370_plus_page_times_376
    fn = fodg_file_size_mod_1471_times_13300_plus_shape_times_373_plus_text_times_370_plus_page_times_376
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1459_importable_from_package():
    from fodg import fodg_file_size_mod_1459_times_13200_plus_shape_times_371_plus_text_times_368_plus_page_times_374
    assert callable(fodg_file_size_mod_1459_times_13200_plus_shape_times_371_plus_text_times_368_plus_page_times_374)


def test_mod1471_importable_from_package():
    from fodg import fodg_file_size_mod_1471_times_13300_plus_shape_times_373_plus_text_times_370_plus_page_times_376
    assert callable(fodg_file_size_mod_1471_times_13300_plus_shape_times_373_plus_text_times_370_plus_page_times_376)
