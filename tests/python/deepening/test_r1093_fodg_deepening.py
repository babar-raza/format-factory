"""Sprint 539 FODG analytics deepening tests — primes 953, 967."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod953_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_953_times_6200_plus_shape_times_231_plus_text_times_228_plus_page_times_234
    assert fodg_file_size_mod_953_times_6200_plus_shape_times_231_plus_text_times_228_plus_page_times_234(str(EMPTY)) == 620234


def test_mod953_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_953_times_6200_plus_shape_times_231_plus_text_times_228_plus_page_times_234
    assert fodg_file_size_mod_953_times_6200_plus_shape_times_231_plus_text_times_228_plus_page_times_234(str(MINIMAL)) == 3224693


def test_mod953_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_953_times_6200_plus_shape_times_231_plus_text_times_228_plus_page_times_234
    assert fodg_file_size_mod_953_times_6200_plus_shape_times_231_plus_text_times_228_plus_page_times_234(str(SHAPES)) == 4186383


def test_mod967_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_967_times_6300_plus_shape_times_233_plus_text_times_230_plus_page_times_236
    assert fodg_file_size_mod_967_times_6300_plus_shape_times_233_plus_text_times_230_plus_page_times_236(str(EMPTY)) == 542036


def test_mod967_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_967_times_6300_plus_shape_times_233_plus_text_times_230_plus_page_times_236
    assert fodg_file_size_mod_967_times_6300_plus_shape_times_233_plus_text_times_230_plus_page_times_236(str(MINIMAL)) == 3188499


def test_mod967_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_967_times_6300_plus_shape_times_233_plus_text_times_230_plus_page_times_236
    assert fodg_file_size_mod_967_times_6300_plus_shape_times_233_plus_text_times_230_plus_page_times_236(str(SHAPES)) == 4165695


def test_mod953_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_953_times_6200_plus_shape_times_231_plus_text_times_228_plus_page_times_234
    assert isinstance(fodg_file_size_mod_953_times_6200_plus_shape_times_231_plus_text_times_228_plus_page_times_234(str(EMPTY)), int)


def test_mod967_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_967_times_6300_plus_shape_times_233_plus_text_times_230_plus_page_times_236
    assert isinstance(fodg_file_size_mod_967_times_6300_plus_shape_times_233_plus_text_times_230_plus_page_times_236(str(EMPTY)), int)


def test_mod953_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_953_times_6200_plus_shape_times_231_plus_text_times_228_plus_page_times_234
    assert fodg_file_size_mod_953_times_6200_plus_shape_times_231_plus_text_times_228_plus_page_times_234(str(EMPTY)) >= 0


def test_mod967_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_967_times_6300_plus_shape_times_233_plus_text_times_230_plus_page_times_236
    assert fodg_file_size_mod_967_times_6300_plus_shape_times_233_plus_text_times_230_plus_page_times_236(str(EMPTY)) >= 0


def test_mod953_importable_from_package():
    from fodg import fodg_file_size_mod_953_times_6200_plus_shape_times_231_plus_text_times_228_plus_page_times_234
    assert callable(fodg_file_size_mod_953_times_6200_plus_shape_times_231_plus_text_times_228_plus_page_times_234)


def test_mod967_importable_from_package():
    from fodg import fodg_file_size_mod_967_times_6300_plus_shape_times_233_plus_text_times_230_plus_page_times_236
    assert callable(fodg_file_size_mod_967_times_6300_plus_shape_times_233_plus_text_times_230_plus_page_times_236)


def test_mod953_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_953_times_6200_plus_shape_times_231_plus_text_times_228_plus_page_times_234
    fn = fodg_file_size_mod_953_times_6200_plus_shape_times_231_plus_text_times_228_plus_page_times_234
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod967_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_967_times_6300_plus_shape_times_233_plus_text_times_230_plus_page_times_236
    fn = fodg_file_size_mod_967_times_6300_plus_shape_times_233_plus_text_times_230_plus_page_times_236
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3
