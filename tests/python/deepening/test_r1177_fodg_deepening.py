"""Sprint 623 FODG analytics deepening tests - primes 1361, 1367."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1361_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1361_times_11800_plus_shape_times_343_plus_text_times_340_plus_page_times_346
    assert fodg_file_size_mod_1361_times_11800_plus_shape_times_343_plus_text_times_340_plus_page_times_346(str(EMPTY)) == 12425746


def test_mod1361_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1361_times_11800_plus_shape_times_343_plus_text_times_340_plus_page_times_346
    assert fodg_file_size_mod_1361_times_11800_plus_shape_times_343_plus_text_times_340_plus_page_times_346(str(MINIMAL)) == 1322629


def test_mod1361_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1361_times_11800_plus_shape_times_343_plus_text_times_340_plus_page_times_346
    assert fodg_file_size_mod_1361_times_11800_plus_shape_times_343_plus_text_times_340_plus_page_times_346(str(SHAPES)) == 3152655


def test_mod1367_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1367_times_11900_plus_shape_times_345_plus_text_times_342_plus_page_times_348
    assert fodg_file_size_mod_1367_times_11900_plus_shape_times_345_plus_text_times_342_plus_page_times_348(str(EMPTY)) == 12531048


def test_mod1367_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1367_times_11900_plus_shape_times_345_plus_text_times_342_plus_page_times_348
    assert fodg_file_size_mod_1367_times_11900_plus_shape_times_345_plus_text_times_342_plus_page_times_348(str(MINIMAL)) == 1262435


def test_mod1367_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1367_times_11900_plus_shape_times_345_plus_text_times_342_plus_page_times_348
    assert fodg_file_size_mod_1367_times_11900_plus_shape_times_345_plus_text_times_342_plus_page_times_348(str(SHAPES)) == 3107967


def test_mod1361_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1361_times_11800_plus_shape_times_343_plus_text_times_340_plus_page_times_346
    assert isinstance(fodg_file_size_mod_1361_times_11800_plus_shape_times_343_plus_text_times_340_plus_page_times_346(str(EMPTY)), int)


def test_mod1367_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1367_times_11900_plus_shape_times_345_plus_text_times_342_plus_page_times_348
    assert isinstance(fodg_file_size_mod_1367_times_11900_plus_shape_times_345_plus_text_times_342_plus_page_times_348(str(EMPTY)), int)


def test_mod1361_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1361_times_11800_plus_shape_times_343_plus_text_times_340_plus_page_times_346
    assert fodg_file_size_mod_1361_times_11800_plus_shape_times_343_plus_text_times_340_plus_page_times_346(str(EMPTY)) >= 0


def test_mod1367_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1367_times_11900_plus_shape_times_345_plus_text_times_342_plus_page_times_348
    assert fodg_file_size_mod_1367_times_11900_plus_shape_times_345_plus_text_times_342_plus_page_times_348(str(EMPTY)) >= 0


def test_mod1361_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1361_times_11800_plus_shape_times_343_plus_text_times_340_plus_page_times_346
    fn = fodg_file_size_mod_1361_times_11800_plus_shape_times_343_plus_text_times_340_plus_page_times_346
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1367_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1367_times_11900_plus_shape_times_345_plus_text_times_342_plus_page_times_348
    fn = fodg_file_size_mod_1367_times_11900_plus_shape_times_345_plus_text_times_342_plus_page_times_348
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1361_importable_from_package():
    from fodg import fodg_file_size_mod_1361_times_11800_plus_shape_times_343_plus_text_times_340_plus_page_times_346
    assert callable(fodg_file_size_mod_1361_times_11800_plus_shape_times_343_plus_text_times_340_plus_page_times_346)


def test_mod1367_importable_from_package():
    from fodg import fodg_file_size_mod_1367_times_11900_plus_shape_times_345_plus_text_times_342_plus_page_times_348
    assert callable(fodg_file_size_mod_1367_times_11900_plus_shape_times_345_plus_text_times_342_plus_page_times_348)
