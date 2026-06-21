"""Sprint 545 FODG analytics deepening tests - primes 983, 991."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod983_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_983_times_6600_plus_shape_times_239_plus_text_times_236_plus_page_times_242
    assert fodg_file_size_mod_983_times_6600_plus_shape_times_239_plus_text_times_236_plus_page_times_242(str(EMPTY)) == 462242


def test_mod983_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_983_times_6600_plus_shape_times_239_plus_text_times_236_plus_page_times_242
    assert fodg_file_size_mod_983_times_6600_plus_shape_times_239_plus_text_times_236_plus_page_times_242(str(MINIMAL)) == 3234717


def test_mod983_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_983_times_6600_plus_shape_times_239_plus_text_times_236_plus_page_times_242
    assert fodg_file_size_mod_983_times_6600_plus_shape_times_239_plus_text_times_236_plus_page_times_242(str(SHAPES)) == 4258431


def test_mod991_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_991_times_6700_plus_shape_times_241_plus_text_times_238_plus_page_times_244
    assert fodg_file_size_mod_991_times_6700_plus_shape_times_241_plus_text_times_238_plus_page_times_244(str(EMPTY)) == 415644


def test_mod991_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_991_times_6700_plus_shape_times_241_plus_text_times_238_plus_page_times_244
    assert fodg_file_size_mod_991_times_6700_plus_shape_times_241_plus_text_times_238_plus_page_times_244(str(MINIMAL)) == 3230123


def test_mod991_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_991_times_6700_plus_shape_times_241_plus_text_times_238_plus_page_times_244
    assert fodg_file_size_mod_991_times_6700_plus_shape_times_241_plus_text_times_238_plus_page_times_244(str(SHAPES)) == 4269343


def test_mod983_returns_int_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_983_times_6600_plus_shape_times_239_plus_text_times_236_plus_page_times_242
    result = fodg_file_size_mod_983_times_6600_plus_shape_times_239_plus_text_times_236_plus_page_times_242(str(EMPTY))
    assert isinstance(result, int)


def test_mod991_returns_int_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_991_times_6700_plus_shape_times_241_plus_text_times_238_plus_page_times_244
    result = fodg_file_size_mod_991_times_6700_plus_shape_times_241_plus_text_times_238_plus_page_times_244(str(MINIMAL))
    assert isinstance(result, int)


def test_mod983_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_983_times_6600_plus_shape_times_239_plus_text_times_236_plus_page_times_242
    assert fodg_file_size_mod_983_times_6600_plus_shape_times_239_plus_text_times_236_plus_page_times_242(str(EMPTY)) >= 0


def test_mod991_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_991_times_6700_plus_shape_times_241_plus_text_times_238_plus_page_times_244
    assert fodg_file_size_mod_991_times_6700_plus_shape_times_241_plus_text_times_238_plus_page_times_244(str(EMPTY)) >= 0


def test_mod983_importable_from_package():
    from fodg import fodg_file_size_mod_983_times_6600_plus_shape_times_239_plus_text_times_236_plus_page_times_242
    assert callable(fodg_file_size_mod_983_times_6600_plus_shape_times_239_plus_text_times_236_plus_page_times_242)


def test_mod991_importable_from_package():
    from fodg import fodg_file_size_mod_991_times_6700_plus_shape_times_241_plus_text_times_238_plus_page_times_244
    assert callable(fodg_file_size_mod_991_times_6700_plus_shape_times_241_plus_text_times_238_plus_page_times_244)


def test_mod983_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_983_times_6600_plus_shape_times_239_plus_text_times_236_plus_page_times_242
    fn = fodg_file_size_mod_983_times_6600_plus_shape_times_239_plus_text_times_236_plus_page_times_242
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod991_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_991_times_6700_plus_shape_times_241_plus_text_times_238_plus_page_times_244
    fn = fodg_file_size_mod_991_times_6700_plus_shape_times_241_plus_text_times_238_plus_page_times_244
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3
