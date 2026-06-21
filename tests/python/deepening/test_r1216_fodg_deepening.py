"""Sprint 662 FODG analytics deepening tests - primes 1549, 1553."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1549_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1549_times_14400_plus_shape_times_395_plus_text_times_392_plus_page_times_398
    assert fodg_file_size_mod_1549_times_14400_plus_shape_times_395_plus_text_times_392_plus_page_times_398(str(EMPTY)) == 15163598


def test_mod1549_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1549_times_14400_plus_shape_times_395_plus_text_times_392_plus_page_times_398
    assert fodg_file_size_mod_1549_times_14400_plus_shape_times_395_plus_text_times_392_plus_page_times_398(str(MINIMAL)) == 21212385


def test_mod1549_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1549_times_14400_plus_shape_times_395_plus_text_times_392_plus_page_times_398
    assert fodg_file_size_mod_1549_times_14400_plus_shape_times_395_plus_text_times_392_plus_page_times_398(str(SHAPES)) == 1139967


def test_mod1553_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1553_times_14500_plus_shape_times_397_plus_text_times_394_plus_page_times_400
    assert fodg_file_size_mod_1553_times_14500_plus_shape_times_397_plus_text_times_394_plus_page_times_400(str(EMPTY)) == 15268900


def test_mod1553_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1553_times_14500_plus_shape_times_397_plus_text_times_394_plus_page_times_400
    assert fodg_file_size_mod_1553_times_14500_plus_shape_times_397_plus_text_times_394_plus_page_times_400(str(MINIMAL)) == 21359691


def test_mod1553_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1553_times_14500_plus_shape_times_397_plus_text_times_394_plus_page_times_400
    assert fodg_file_size_mod_1553_times_14500_plus_shape_times_397_plus_text_times_394_plus_page_times_400(str(SHAPES)) == 1089879


def test_mod1549_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1549_times_14400_plus_shape_times_395_plus_text_times_392_plus_page_times_398
    assert isinstance(fodg_file_size_mod_1549_times_14400_plus_shape_times_395_plus_text_times_392_plus_page_times_398(str(EMPTY)), int)


def test_mod1553_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1553_times_14500_plus_shape_times_397_plus_text_times_394_plus_page_times_400
    assert isinstance(fodg_file_size_mod_1553_times_14500_plus_shape_times_397_plus_text_times_394_plus_page_times_400(str(EMPTY)), int)


def test_mod1549_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1549_times_14400_plus_shape_times_395_plus_text_times_392_plus_page_times_398
    assert fodg_file_size_mod_1549_times_14400_plus_shape_times_395_plus_text_times_392_plus_page_times_398(str(EMPTY)) >= 0


def test_mod1553_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1553_times_14500_plus_shape_times_397_plus_text_times_394_plus_page_times_400
    assert fodg_file_size_mod_1553_times_14500_plus_shape_times_397_plus_text_times_394_plus_page_times_400(str(EMPTY)) >= 0


def test_mod1549_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1549_times_14400_plus_shape_times_395_plus_text_times_392_plus_page_times_398
    fn = fodg_file_size_mod_1549_times_14400_plus_shape_times_395_plus_text_times_392_plus_page_times_398
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1553_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1553_times_14500_plus_shape_times_397_plus_text_times_394_plus_page_times_400
    fn = fodg_file_size_mod_1553_times_14500_plus_shape_times_397_plus_text_times_394_plus_page_times_400
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1549_importable_from_package():
    from fodg import fodg_file_size_mod_1549_times_14400_plus_shape_times_395_plus_text_times_392_plus_page_times_398
    assert callable(fodg_file_size_mod_1549_times_14400_plus_shape_times_395_plus_text_times_392_plus_page_times_398)


def test_mod1553_importable_from_package():
    from fodg import fodg_file_size_mod_1553_times_14500_plus_shape_times_397_plus_text_times_394_plus_page_times_400
    assert callable(fodg_file_size_mod_1553_times_14500_plus_shape_times_397_plus_text_times_394_plus_page_times_400)
