"""Sprint 554 FODG analytics deepening tests - primes 1021, 1031."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1021_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1021_times_7200_plus_shape_times_251_plus_text_times_248_plus_page_times_254
    assert fodg_file_size_mod_1021_times_7200_plus_shape_times_251_plus_text_times_248_plus_page_times_254(str(EMPTY)) == 230654


def test_mod1021_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1021_times_7200_plus_shape_times_251_plus_text_times_248_plus_page_times_254
    assert fodg_file_size_mod_1021_times_7200_plus_shape_times_251_plus_text_times_248_plus_page_times_254(str(MINIMAL)) == 3255153


def test_mod1021_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1021_times_7200_plus_shape_times_251_plus_text_times_248_plus_page_times_254
    assert fodg_file_size_mod_1021_times_7200_plus_shape_times_251_plus_text_times_248_plus_page_times_254(str(SHAPES)) == 4371903


def test_mod1031_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1031_times_7300_plus_shape_times_253_plus_text_times_250_plus_page_times_256
    assert fodg_file_size_mod_1031_times_7300_plus_shape_times_253_plus_text_times_250_plus_page_times_256(str(EMPTY)) == 160856


def test_mod1031_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1031_times_7300_plus_shape_times_253_plus_text_times_250_plus_page_times_256
    assert fodg_file_size_mod_1031_times_7300_plus_shape_times_253_plus_text_times_250_plus_page_times_256(str(MINIMAL)) == 3227359


def test_mod1031_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1031_times_7300_plus_shape_times_253_plus_text_times_250_plus_page_times_256
    assert fodg_file_size_mod_1031_times_7300_plus_shape_times_253_plus_text_times_250_plus_page_times_256(str(SHAPES)) == 4359615


def test_mod1021_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1021_times_7200_plus_shape_times_251_plus_text_times_248_plus_page_times_254
    assert isinstance(fodg_file_size_mod_1021_times_7200_plus_shape_times_251_plus_text_times_248_plus_page_times_254(str(EMPTY)), int)


def test_mod1031_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1031_times_7300_plus_shape_times_253_plus_text_times_250_plus_page_times_256
    assert isinstance(fodg_file_size_mod_1031_times_7300_plus_shape_times_253_plus_text_times_250_plus_page_times_256(str(EMPTY)), int)


def test_mod1021_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1021_times_7200_plus_shape_times_251_plus_text_times_248_plus_page_times_254
    assert fodg_file_size_mod_1021_times_7200_plus_shape_times_251_plus_text_times_248_plus_page_times_254(str(EMPTY)) >= 0


def test_mod1031_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1031_times_7300_plus_shape_times_253_plus_text_times_250_plus_page_times_256
    assert fodg_file_size_mod_1031_times_7300_plus_shape_times_253_plus_text_times_250_plus_page_times_256(str(EMPTY)) >= 0


def test_mod1021_importable_from_package():
    from fodg import fodg_file_size_mod_1021_times_7200_plus_shape_times_251_plus_text_times_248_plus_page_times_254
    assert callable(fodg_file_size_mod_1021_times_7200_plus_shape_times_251_plus_text_times_248_plus_page_times_254)


def test_mod1031_importable_from_package():
    from fodg import fodg_file_size_mod_1031_times_7300_plus_shape_times_253_plus_text_times_250_plus_page_times_256
    assert callable(fodg_file_size_mod_1031_times_7300_plus_shape_times_253_plus_text_times_250_plus_page_times_256)


def test_mod1021_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1021_times_7200_plus_shape_times_251_plus_text_times_248_plus_page_times_254
    fn = fodg_file_size_mod_1021_times_7200_plus_shape_times_251_plus_text_times_248_plus_page_times_254
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1031_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1031_times_7300_plus_shape_times_253_plus_text_times_250_plus_page_times_256
    fn = fodg_file_size_mod_1031_times_7300_plus_shape_times_253_plus_text_times_250_plus_page_times_256
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3
