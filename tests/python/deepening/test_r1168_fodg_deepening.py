"""Sprint 614 FODG analytics deepening tests - primes 1301, 1303."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1301_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1301_times_11200_plus_shape_times_331_plus_text_times_328_plus_page_times_334
    assert fodg_file_size_mod_1301_times_11200_plus_shape_times_331_plus_text_times_328_plus_page_times_334(str(EMPTY)) == 11793934


def test_mod1301_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1301_times_11200_plus_shape_times_331_plus_text_times_328_plus_page_times_334
    assert fodg_file_size_mod_1301_times_11200_plus_shape_times_331_plus_text_times_328_plus_page_times_334(str(MINIMAL)) == 1927393


def test_mod1301_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1301_times_11200_plus_shape_times_331_plus_text_times_328_plus_page_times_334
    assert fodg_file_size_mod_1301_times_11200_plus_shape_times_331_plus_text_times_328_plus_page_times_334(str(SHAPES)) == 3664383


def test_mod1303_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1303_times_11300_plus_shape_times_333_plus_text_times_330_plus_page_times_336
    assert fodg_file_size_mod_1303_times_11300_plus_shape_times_333_plus_text_times_330_plus_page_times_336(str(EMPTY)) == 11899236


def test_mod1303_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1303_times_11300_plus_shape_times_333_plus_text_times_330_plus_page_times_336
    assert fodg_file_size_mod_1303_times_11300_plus_shape_times_333_plus_text_times_330_plus_page_times_336(str(MINIMAL)) == 1921999


def test_mod1303_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1303_times_11300_plus_shape_times_333_plus_text_times_330_plus_page_times_336
    assert fodg_file_size_mod_1303_times_11300_plus_shape_times_333_plus_text_times_330_plus_page_times_336(str(SHAPES)) == 3674495


def test_mod1301_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1301_times_11200_plus_shape_times_331_plus_text_times_328_plus_page_times_334
    assert isinstance(fodg_file_size_mod_1301_times_11200_plus_shape_times_331_plus_text_times_328_plus_page_times_334(str(EMPTY)), int)


def test_mod1303_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1303_times_11300_plus_shape_times_333_plus_text_times_330_plus_page_times_336
    assert isinstance(fodg_file_size_mod_1303_times_11300_plus_shape_times_333_plus_text_times_330_plus_page_times_336(str(EMPTY)), int)


def test_mod1301_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1301_times_11200_plus_shape_times_331_plus_text_times_328_plus_page_times_334
    assert fodg_file_size_mod_1301_times_11200_plus_shape_times_331_plus_text_times_328_plus_page_times_334(str(EMPTY)) >= 0


def test_mod1303_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1303_times_11300_plus_shape_times_333_plus_text_times_330_plus_page_times_336
    assert fodg_file_size_mod_1303_times_11300_plus_shape_times_333_plus_text_times_330_plus_page_times_336(str(EMPTY)) >= 0


def test_mod1301_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1301_times_11200_plus_shape_times_331_plus_text_times_328_plus_page_times_334
    fn = fodg_file_size_mod_1301_times_11200_plus_shape_times_331_plus_text_times_328_plus_page_times_334
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1303_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1303_times_11300_plus_shape_times_333_plus_text_times_330_plus_page_times_336
    fn = fodg_file_size_mod_1303_times_11300_plus_shape_times_333_plus_text_times_330_plus_page_times_336
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1301_importable_from_package():
    from fodg import fodg_file_size_mod_1301_times_11200_plus_shape_times_331_plus_text_times_328_plus_page_times_334
    assert callable(fodg_file_size_mod_1301_times_11200_plus_shape_times_331_plus_text_times_328_plus_page_times_334)


def test_mod1303_importable_from_package():
    from fodg import fodg_file_size_mod_1303_times_11300_plus_shape_times_333_plus_text_times_330_plus_page_times_336
    assert callable(fodg_file_size_mod_1303_times_11300_plus_shape_times_333_plus_text_times_330_plus_page_times_336)
