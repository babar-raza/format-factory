"""Sprint 653 FODG analytics deepening tests - primes 1493, 1499."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1493_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1493_times_13800_plus_shape_times_383_plus_text_times_380_plus_page_times_386
    assert fodg_file_size_mod_1493_times_13800_plus_shape_times_383_plus_text_times_380_plus_page_times_386(str(EMPTY)) == 14531786


def test_mod1493_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1493_times_13800_plus_shape_times_383_plus_text_times_380_plus_page_times_386
    assert fodg_file_size_mod_1493_times_13800_plus_shape_times_383_plus_text_times_380_plus_page_times_386(str(MINIMAL)) == 20328549


def test_mod1493_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1493_times_13800_plus_shape_times_383_plus_text_times_380_plus_page_times_386
    assert fodg_file_size_mod_1493_times_13800_plus_shape_times_383_plus_text_times_380_plus_page_times_386(str(SHAPES)) == 1865295


def test_mod1499_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1499_times_13900_plus_shape_times_385_plus_text_times_382_plus_page_times_388
    assert fodg_file_size_mod_1499_times_13900_plus_shape_times_385_plus_text_times_382_plus_page_times_388(str(EMPTY)) == 14637088


def test_mod1499_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1499_times_13900_plus_shape_times_385_plus_text_times_382_plus_page_times_388
    assert fodg_file_size_mod_1499_times_13900_plus_shape_times_385_plus_text_times_382_plus_page_times_388(str(MINIMAL)) == 20475855


def test_mod1499_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1499_times_13900_plus_shape_times_385_plus_text_times_382_plus_page_times_388
    assert fodg_file_size_mod_1499_times_13900_plus_shape_times_385_plus_text_times_382_plus_page_times_388(str(SHAPES)) == 1795407


def test_mod1493_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1493_times_13800_plus_shape_times_383_plus_text_times_380_plus_page_times_386
    assert isinstance(fodg_file_size_mod_1493_times_13800_plus_shape_times_383_plus_text_times_380_plus_page_times_386(str(EMPTY)), int)


def test_mod1499_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1499_times_13900_plus_shape_times_385_plus_text_times_382_plus_page_times_388
    assert isinstance(fodg_file_size_mod_1499_times_13900_plus_shape_times_385_plus_text_times_382_plus_page_times_388(str(EMPTY)), int)


def test_mod1493_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1493_times_13800_plus_shape_times_383_plus_text_times_380_plus_page_times_386
    assert fodg_file_size_mod_1493_times_13800_plus_shape_times_383_plus_text_times_380_plus_page_times_386(str(EMPTY)) >= 0


def test_mod1499_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1499_times_13900_plus_shape_times_385_plus_text_times_382_plus_page_times_388
    assert fodg_file_size_mod_1499_times_13900_plus_shape_times_385_plus_text_times_382_plus_page_times_388(str(EMPTY)) >= 0


def test_mod1493_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1493_times_13800_plus_shape_times_383_plus_text_times_380_plus_page_times_386
    fn = fodg_file_size_mod_1493_times_13800_plus_shape_times_383_plus_text_times_380_plus_page_times_386
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1499_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1499_times_13900_plus_shape_times_385_plus_text_times_382_plus_page_times_388
    fn = fodg_file_size_mod_1499_times_13900_plus_shape_times_385_plus_text_times_382_plus_page_times_388
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1493_importable_from_package():
    from fodg import fodg_file_size_mod_1493_times_13800_plus_shape_times_383_plus_text_times_380_plus_page_times_386
    assert callable(fodg_file_size_mod_1493_times_13800_plus_shape_times_383_plus_text_times_380_plus_page_times_386)


def test_mod1499_importable_from_package():
    from fodg import fodg_file_size_mod_1499_times_13900_plus_shape_times_385_plus_text_times_382_plus_page_times_388
    assert callable(fodg_file_size_mod_1499_times_13900_plus_shape_times_385_plus_text_times_382_plus_page_times_388)
