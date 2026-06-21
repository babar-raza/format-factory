"""Sprint 542 FODG analytics deepening tests — primes 971, 977."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod971_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_971_times_6400_plus_shape_times_235_plus_text_times_232_plus_page_times_238
    assert fodg_file_size_mod_971_times_6400_plus_shape_times_235_plus_text_times_232_plus_page_times_238(str(EMPTY)) == 525038


def test_mod971_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_971_times_6400_plus_shape_times_235_plus_text_times_232_plus_page_times_238
    assert fodg_file_size_mod_971_times_6400_plus_shape_times_235_plus_text_times_232_plus_page_times_238(str(MINIMAL)) == 3213505


def test_mod971_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_971_times_6400_plus_shape_times_235_plus_text_times_232_plus_page_times_238
    assert fodg_file_size_mod_971_times_6400_plus_shape_times_235_plus_text_times_232_plus_page_times_238(str(SHAPES)) == 4206207


def test_mod977_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_977_times_6500_plus_shape_times_237_plus_text_times_234_plus_page_times_240
    assert fodg_file_size_mod_977_times_6500_plus_shape_times_237_plus_text_times_234_plus_page_times_240(str(EMPTY)) == 494240


def test_mod977_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_977_times_6500_plus_shape_times_237_plus_text_times_234_plus_page_times_240
    assert fodg_file_size_mod_977_times_6500_plus_shape_times_237_plus_text_times_234_plus_page_times_240(str(MINIMAL)) == 3224711


def test_mod977_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_977_times_6500_plus_shape_times_237_plus_text_times_234_plus_page_times_240
    assert fodg_file_size_mod_977_times_6500_plus_shape_times_237_plus_text_times_234_plus_page_times_240(str(SHAPES)) == 4232919


def test_mod971_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_971_times_6400_plus_shape_times_235_plus_text_times_232_plus_page_times_238
    assert isinstance(fodg_file_size_mod_971_times_6400_plus_shape_times_235_plus_text_times_232_plus_page_times_238(str(EMPTY)), int)


def test_mod977_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_977_times_6500_plus_shape_times_237_plus_text_times_234_plus_page_times_240
    assert isinstance(fodg_file_size_mod_977_times_6500_plus_shape_times_237_plus_text_times_234_plus_page_times_240(str(EMPTY)), int)


def test_mod971_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_971_times_6400_plus_shape_times_235_plus_text_times_232_plus_page_times_238
    assert fodg_file_size_mod_971_times_6400_plus_shape_times_235_plus_text_times_232_plus_page_times_238(str(EMPTY)) >= 0


def test_mod977_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_977_times_6500_plus_shape_times_237_plus_text_times_234_plus_page_times_240
    assert fodg_file_size_mod_977_times_6500_plus_shape_times_237_plus_text_times_234_plus_page_times_240(str(EMPTY)) >= 0


def test_mod971_importable_from_package():
    from fodg import fodg_file_size_mod_971_times_6400_plus_shape_times_235_plus_text_times_232_plus_page_times_238
    assert callable(fodg_file_size_mod_971_times_6400_plus_shape_times_235_plus_text_times_232_plus_page_times_238)


def test_mod977_importable_from_package():
    from fodg import fodg_file_size_mod_977_times_6500_plus_shape_times_237_plus_text_times_234_plus_page_times_240
    assert callable(fodg_file_size_mod_977_times_6500_plus_shape_times_237_plus_text_times_234_plus_page_times_240)


def test_mod971_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_971_times_6400_plus_shape_times_235_plus_text_times_232_plus_page_times_238
    fn = fodg_file_size_mod_971_times_6400_plus_shape_times_235_plus_text_times_232_plus_page_times_238
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod977_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_977_times_6500_plus_shape_times_237_plus_text_times_234_plus_page_times_240
    fn = fodg_file_size_mod_977_times_6500_plus_shape_times_237_plus_text_times_234_plus_page_times_240
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3
