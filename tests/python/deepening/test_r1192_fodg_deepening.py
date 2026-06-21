"""Sprint 638 FODG analytics deepening tests - primes 1439, 1447."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1439_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1439_times_12800_plus_shape_times_363_plus_text_times_360_plus_page_times_366
    assert fodg_file_size_mod_1439_times_12800_plus_shape_times_363_plus_text_times_360_plus_page_times_366(str(EMPTY)) == 13478766


def test_mod1439_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1439_times_12800_plus_shape_times_363_plus_text_times_360_plus_page_times_366
    assert fodg_file_size_mod_1439_times_12800_plus_shape_times_363_plus_text_times_360_plus_page_times_366(str(MINIMAL)) == 436289


def test_mod1439_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1439_times_12800_plus_shape_times_363_plus_text_times_360_plus_page_times_366
    assert fodg_file_size_mod_1439_times_12800_plus_shape_times_363_plus_text_times_360_plus_page_times_366(str(SHAPES)) == 2421375


def test_mod1439_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1439_times_12800_plus_shape_times_363_plus_text_times_360_plus_page_times_366
    assert isinstance(fodg_file_size_mod_1439_times_12800_plus_shape_times_363_plus_text_times_360_plus_page_times_366(str(EMPTY)), int)


def test_mod1439_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1439_times_12800_plus_shape_times_363_plus_text_times_360_plus_page_times_366
    assert fodg_file_size_mod_1439_times_12800_plus_shape_times_363_plus_text_times_360_plus_page_times_366(str(EMPTY)) >= 0


def test_mod1439_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1439_times_12800_plus_shape_times_363_plus_text_times_360_plus_page_times_366
    fn_ref = fodg_file_size_mod_1439_times_12800_plus_shape_times_363_plus_text_times_360_plus_page_times_366
    results = {fn_ref(str(EMPTY)), fn_ref(str(MINIMAL)), fn_ref(str(SHAPES))}
    assert len(results) == 3


def test_mod1439_importable_from_package():
    from fodg import fodg_file_size_mod_1439_times_12800_plus_shape_times_363_plus_text_times_360_plus_page_times_366
    assert callable(fodg_file_size_mod_1439_times_12800_plus_shape_times_363_plus_text_times_360_plus_page_times_366)


def test_mod1447_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1447_times_12900_plus_shape_times_365_plus_text_times_362_plus_page_times_368
    assert fodg_file_size_mod_1447_times_12900_plus_shape_times_365_plus_text_times_362_plus_page_times_368(str(EMPTY)) == 13584068


def test_mod1447_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1447_times_12900_plus_shape_times_365_plus_text_times_362_plus_page_times_368
    assert fodg_file_size_mod_1447_times_12900_plus_shape_times_365_plus_text_times_362_plus_page_times_368(str(MINIMAL)) == 336495


def test_mod1447_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1447_times_12900_plus_shape_times_365_plus_text_times_362_plus_page_times_368
    assert fodg_file_size_mod_1447_times_12900_plus_shape_times_365_plus_text_times_362_plus_page_times_368(str(SHAPES)) == 2337087


def test_mod1447_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1447_times_12900_plus_shape_times_365_plus_text_times_362_plus_page_times_368
    assert isinstance(fodg_file_size_mod_1447_times_12900_plus_shape_times_365_plus_text_times_362_plus_page_times_368(str(EMPTY)), int)


def test_mod1447_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1447_times_12900_plus_shape_times_365_plus_text_times_362_plus_page_times_368
    assert fodg_file_size_mod_1447_times_12900_plus_shape_times_365_plus_text_times_362_plus_page_times_368(str(EMPTY)) >= 0


def test_mod1447_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1447_times_12900_plus_shape_times_365_plus_text_times_362_plus_page_times_368
    fn_ref = fodg_file_size_mod_1447_times_12900_plus_shape_times_365_plus_text_times_362_plus_page_times_368
    results = {fn_ref(str(EMPTY)), fn_ref(str(MINIMAL)), fn_ref(str(SHAPES))}
    assert len(results) == 3


def test_mod1447_importable_from_package():
    from fodg import fodg_file_size_mod_1447_times_12900_plus_shape_times_365_plus_text_times_362_plus_page_times_368
    assert callable(fodg_file_size_mod_1447_times_12900_plus_shape_times_365_plus_text_times_362_plus_page_times_368)
