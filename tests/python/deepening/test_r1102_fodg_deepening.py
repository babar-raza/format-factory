"""Sprint 548 FODG analytics deepening tests - primes 997, 1009."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod997_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_997_times_6800_plus_shape_times_243_plus_text_times_240_plus_page_times_246
    assert fodg_file_size_mod_997_times_6800_plus_shape_times_243_plus_text_times_240_plus_page_times_246(str(EMPTY)) == 381046


def test_mod997_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_997_times_6800_plus_shape_times_243_plus_text_times_240_plus_page_times_246
    assert fodg_file_size_mod_997_times_6800_plus_shape_times_243_plus_text_times_240_plus_page_times_246(str(MINIMAL)) == 3237529


def test_mod997_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_997_times_6800_plus_shape_times_243_plus_text_times_240_plus_page_times_246
    assert fodg_file_size_mod_997_times_6800_plus_shape_times_243_plus_text_times_240_plus_page_times_246(str(SHAPES)) == 4292255


def test_mod1009_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1009_times_6900_plus_shape_times_245_plus_text_times_242_plus_page_times_248
    assert fodg_file_size_mod_1009_times_6900_plus_shape_times_245_plus_text_times_242_plus_page_times_248(str(EMPTY)) == 303848


def test_mod1009_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1009_times_6900_plus_shape_times_245_plus_text_times_242_plus_page_times_248
    assert fodg_file_size_mod_1009_times_6900_plus_shape_times_245_plus_text_times_242_plus_page_times_248(str(MINIMAL)) == 3202335


def test_mod1009_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1009_times_6900_plus_shape_times_245_plus_text_times_242_plus_page_times_248
    assert fodg_file_size_mod_1009_times_6900_plus_shape_times_245_plus_text_times_242_plus_page_times_248(str(SHAPES)) == 4272567


def test_mod997_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_997_times_6800_plus_shape_times_243_plus_text_times_240_plus_page_times_246
    assert isinstance(fodg_file_size_mod_997_times_6800_plus_shape_times_243_plus_text_times_240_plus_page_times_246(str(EMPTY)), int)


def test_mod1009_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1009_times_6900_plus_shape_times_245_plus_text_times_242_plus_page_times_248
    assert isinstance(fodg_file_size_mod_1009_times_6900_plus_shape_times_245_plus_text_times_242_plus_page_times_248(str(EMPTY)), int)


def test_mod997_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_997_times_6800_plus_shape_times_243_plus_text_times_240_plus_page_times_246
    assert fodg_file_size_mod_997_times_6800_plus_shape_times_243_plus_text_times_240_plus_page_times_246(str(EMPTY)) >= 0


def test_mod1009_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1009_times_6900_plus_shape_times_245_plus_text_times_242_plus_page_times_248
    assert fodg_file_size_mod_1009_times_6900_plus_shape_times_245_plus_text_times_242_plus_page_times_248(str(EMPTY)) >= 0


def test_mod997_importable_from_package():
    from fodg import fodg_file_size_mod_997_times_6800_plus_shape_times_243_plus_text_times_240_plus_page_times_246
    assert callable(fodg_file_size_mod_997_times_6800_plus_shape_times_243_plus_text_times_240_plus_page_times_246)


def test_mod1009_importable_from_package():
    from fodg import fodg_file_size_mod_1009_times_6900_plus_shape_times_245_plus_text_times_242_plus_page_times_248
    assert callable(fodg_file_size_mod_1009_times_6900_plus_shape_times_245_plus_text_times_242_plus_page_times_248)


def test_mod997_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_997_times_6800_plus_shape_times_243_plus_text_times_240_plus_page_times_246
    fn = fodg_file_size_mod_997_times_6800_plus_shape_times_243_plus_text_times_240_plus_page_times_246
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1009_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1009_times_6900_plus_shape_times_245_plus_text_times_242_plus_page_times_248
    fn = fodg_file_size_mod_1009_times_6900_plus_shape_times_245_plus_text_times_242_plus_page_times_248
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3
