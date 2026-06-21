"""Sprint 536 FODG analytics deepening tests — primes 941, 947."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod941_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_941_times_6000_plus_shape_times_227_plus_text_times_224_plus_page_times_230
    assert fodg_file_size_mod_941_times_6000_plus_shape_times_227_plus_text_times_224_plus_page_times_230(str(EMPTY)) == 672230


def test_mod941_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_941_times_6000_plus_shape_times_227_plus_text_times_224_plus_page_times_230
    assert fodg_file_size_mod_941_times_6000_plus_shape_times_227_plus_text_times_224_plus_page_times_230(str(MINIMAL)) == 3192681


def test_mod941_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_941_times_6000_plus_shape_times_227_plus_text_times_224_plus_page_times_230
    assert fodg_file_size_mod_941_times_6000_plus_shape_times_227_plus_text_times_224_plus_page_times_230(str(SHAPES)) == 4123359


def test_mod947_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_947_times_6100_plus_shape_times_229_plus_text_times_226_plus_page_times_232
    assert fodg_file_size_mod_947_times_6100_plus_shape_times_229_plus_text_times_226_plus_page_times_232(str(EMPTY)) == 646832


def test_mod947_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_947_times_6100_plus_shape_times_229_plus_text_times_226_plus_page_times_232
    assert fodg_file_size_mod_947_times_6100_plus_shape_times_229_plus_text_times_226_plus_page_times_232(str(MINIMAL)) == 3209287


def test_mod947_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_947_times_6100_plus_shape_times_229_plus_text_times_226_plus_page_times_232
    assert fodg_file_size_mod_947_times_6100_plus_shape_times_229_plus_text_times_226_plus_page_times_232(str(SHAPES)) == 4155471


def test_mod941_returns_int_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_941_times_6000_plus_shape_times_227_plus_text_times_224_plus_page_times_230
    result = fodg_file_size_mod_941_times_6000_plus_shape_times_227_plus_text_times_224_plus_page_times_230(str(EMPTY))
    assert isinstance(result, int)


def test_mod947_returns_int_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_947_times_6100_plus_shape_times_229_plus_text_times_226_plus_page_times_232
    result = fodg_file_size_mod_947_times_6100_plus_shape_times_229_plus_text_times_226_plus_page_times_232(str(MINIMAL))
    assert isinstance(result, int)


def test_mod941_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_941_times_6000_plus_shape_times_227_plus_text_times_224_plus_page_times_230
    assert fodg_file_size_mod_941_times_6000_plus_shape_times_227_plus_text_times_224_plus_page_times_230(str(EMPTY)) >= 0


def test_mod947_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_947_times_6100_plus_shape_times_229_plus_text_times_226_plus_page_times_232
    assert fodg_file_size_mod_947_times_6100_plus_shape_times_229_plus_text_times_226_plus_page_times_232(str(EMPTY)) >= 0


def test_mod941_importable_from_package():
    from fodg import fodg_file_size_mod_941_times_6000_plus_shape_times_227_plus_text_times_224_plus_page_times_230
    assert callable(fodg_file_size_mod_941_times_6000_plus_shape_times_227_plus_text_times_224_plus_page_times_230)


def test_mod947_importable_from_package():
    from fodg import fodg_file_size_mod_947_times_6100_plus_shape_times_229_plus_text_times_226_plus_page_times_232
    assert callable(fodg_file_size_mod_947_times_6100_plus_shape_times_229_plus_text_times_226_plus_page_times_232)


def test_mod941_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_941_times_6000_plus_shape_times_227_plus_text_times_224_plus_page_times_230
    fn = fodg_file_size_mod_941_times_6000_plus_shape_times_227_plus_text_times_224_plus_page_times_230
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod947_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_947_times_6100_plus_shape_times_229_plus_text_times_226_plus_page_times_232
    fn = fodg_file_size_mod_947_times_6100_plus_shape_times_229_plus_text_times_226_plus_page_times_232
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3
