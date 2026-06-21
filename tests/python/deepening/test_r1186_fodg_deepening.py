"""Sprint 632 FODG analytics deepening tests - primes 1423, 1427."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1423_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1423_times_12400_plus_shape_times_355_plus_text_times_352_plus_page_times_358
    assert fodg_file_size_mod_1423_times_12400_plus_shape_times_355_plus_text_times_352_plus_page_times_358(str(EMPTY)) == 13057558


def test_mod1423_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1423_times_12400_plus_shape_times_355_plus_text_times_352_plus_page_times_358
    assert fodg_file_size_mod_1423_times_12400_plus_shape_times_355_plus_text_times_352_plus_page_times_358(str(MINIMAL)) == 621065


def test_mod1423_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1423_times_12400_plus_shape_times_355_plus_text_times_352_plus_page_times_358
    assert fodg_file_size_mod_1423_times_12400_plus_shape_times_355_plus_text_times_352_plus_page_times_358(str(SHAPES)) == 2544127


def test_mod1423_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1423_times_12400_plus_shape_times_355_plus_text_times_352_plus_page_times_358
    assert isinstance(fodg_file_size_mod_1423_times_12400_plus_shape_times_355_plus_text_times_352_plus_page_times_358(str(EMPTY)), int)


def test_mod1423_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1423_times_12400_plus_shape_times_355_plus_text_times_352_plus_page_times_358
    assert fodg_file_size_mod_1423_times_12400_plus_shape_times_355_plus_text_times_352_plus_page_times_358(str(EMPTY)) >= 0


def test_mod1423_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1423_times_12400_plus_shape_times_355_plus_text_times_352_plus_page_times_358
    fn_ref = fodg_file_size_mod_1423_times_12400_plus_shape_times_355_plus_text_times_352_plus_page_times_358
    results = {fn_ref(str(EMPTY)), fn_ref(str(MINIMAL)), fn_ref(str(SHAPES))}
    assert len(results) == 3


def test_mod1423_importable_from_package():
    from fodg import fodg_file_size_mod_1423_times_12400_plus_shape_times_355_plus_text_times_352_plus_page_times_358
    assert callable(fodg_file_size_mod_1423_times_12400_plus_shape_times_355_plus_text_times_352_plus_page_times_358)


def test_mod1427_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1427_times_12500_plus_shape_times_357_plus_text_times_354_plus_page_times_360
    assert fodg_file_size_mod_1427_times_12500_plus_shape_times_357_plus_text_times_354_plus_page_times_360(str(EMPTY)) == 13162860


def test_mod1427_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1427_times_12500_plus_shape_times_357_plus_text_times_354_plus_page_times_360
    assert fodg_file_size_mod_1427_times_12500_plus_shape_times_357_plus_text_times_354_plus_page_times_360(str(MINIMAL)) == 576071


def test_mod1427_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1427_times_12500_plus_shape_times_357_plus_text_times_354_plus_page_times_360
    assert fodg_file_size_mod_1427_times_12500_plus_shape_times_357_plus_text_times_354_plus_page_times_360(str(SHAPES)) == 2514639


def test_mod1427_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1427_times_12500_plus_shape_times_357_plus_text_times_354_plus_page_times_360
    assert isinstance(fodg_file_size_mod_1427_times_12500_plus_shape_times_357_plus_text_times_354_plus_page_times_360(str(EMPTY)), int)


def test_mod1427_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1427_times_12500_plus_shape_times_357_plus_text_times_354_plus_page_times_360
    assert fodg_file_size_mod_1427_times_12500_plus_shape_times_357_plus_text_times_354_plus_page_times_360(str(EMPTY)) >= 0


def test_mod1427_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1427_times_12500_plus_shape_times_357_plus_text_times_354_plus_page_times_360
    fn_ref = fodg_file_size_mod_1427_times_12500_plus_shape_times_357_plus_text_times_354_plus_page_times_360
    results = {fn_ref(str(EMPTY)), fn_ref(str(MINIMAL)), fn_ref(str(SHAPES))}
    assert len(results) == 3


def test_mod1427_importable_from_package():
    from fodg import fodg_file_size_mod_1427_times_12500_plus_shape_times_357_plus_text_times_354_plus_page_times_360
    assert callable(fodg_file_size_mod_1427_times_12500_plus_shape_times_357_plus_text_times_354_plus_page_times_360)
