"""Sprint 641 FODG analytics deepening tests - primes 1451, 1453."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1451_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1451_times_13000_plus_shape_times_367_plus_text_times_364_plus_page_times_370
    assert fodg_file_size_mod_1451_times_13000_plus_shape_times_367_plus_text_times_364_plus_page_times_370(str(EMPTY)) == 13689370


def test_mod1451_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1451_times_13000_plus_shape_times_367_plus_text_times_364_plus_page_times_370
    assert fodg_file_size_mod_1451_times_13000_plus_shape_times_367_plus_text_times_364_plus_page_times_370(str(MINIMAL)) == 287101


def test_mod1451_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1451_times_13000_plus_shape_times_367_plus_text_times_364_plus_page_times_370
    assert fodg_file_size_mod_1451_times_13000_plus_shape_times_367_plus_text_times_364_plus_page_times_370(str(SHAPES)) == 2303199


def test_mod1453_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1453_times_13100_plus_shape_times_369_plus_text_times_366_plus_page_times_372
    assert fodg_file_size_mod_1453_times_13100_plus_shape_times_369_plus_text_times_366_plus_page_times_372(str(EMPTY)) == 13794672


def test_mod1453_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1453_times_13100_plus_shape_times_369_plus_text_times_366_plus_page_times_372
    assert fodg_file_size_mod_1453_times_13100_plus_shape_times_369_plus_text_times_366_plus_page_times_372(str(MINIMAL)) == 263107


def test_mod1453_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1453_times_13100_plus_shape_times_369_plus_text_times_366_plus_page_times_372
    assert fodg_file_size_mod_1453_times_13100_plus_shape_times_369_plus_text_times_366_plus_page_times_372(str(SHAPES)) == 2294711


def test_mod1451_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1451_times_13000_plus_shape_times_367_plus_text_times_364_plus_page_times_370
    assert isinstance(fodg_file_size_mod_1451_times_13000_plus_shape_times_367_plus_text_times_364_plus_page_times_370(str(EMPTY)), int)


def test_mod1453_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1453_times_13100_plus_shape_times_369_plus_text_times_366_plus_page_times_372
    assert isinstance(fodg_file_size_mod_1453_times_13100_plus_shape_times_369_plus_text_times_366_plus_page_times_372(str(EMPTY)), int)


def test_mod1451_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1451_times_13000_plus_shape_times_367_plus_text_times_364_plus_page_times_370
    assert fodg_file_size_mod_1451_times_13000_plus_shape_times_367_plus_text_times_364_plus_page_times_370(str(EMPTY)) >= 0


def test_mod1453_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1453_times_13100_plus_shape_times_369_plus_text_times_366_plus_page_times_372
    assert fodg_file_size_mod_1453_times_13100_plus_shape_times_369_plus_text_times_366_plus_page_times_372(str(EMPTY)) >= 0


def test_mod1451_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1451_times_13000_plus_shape_times_367_plus_text_times_364_plus_page_times_370
    fn = fodg_file_size_mod_1451_times_13000_plus_shape_times_367_plus_text_times_364_plus_page_times_370
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1453_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1453_times_13100_plus_shape_times_369_plus_text_times_366_plus_page_times_372
    fn = fodg_file_size_mod_1453_times_13100_plus_shape_times_369_plus_text_times_366_plus_page_times_372
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1451_importable_from_package():
    from fodg import fodg_file_size_mod_1451_times_13000_plus_shape_times_367_plus_text_times_364_plus_page_times_370
    assert callable(fodg_file_size_mod_1451_times_13000_plus_shape_times_367_plus_text_times_364_plus_page_times_370)


def test_mod1453_importable_from_package():
    from fodg import fodg_file_size_mod_1453_times_13100_plus_shape_times_369_plus_text_times_366_plus_page_times_372
    assert callable(fodg_file_size_mod_1453_times_13100_plus_shape_times_369_plus_text_times_366_plus_page_times_372)
