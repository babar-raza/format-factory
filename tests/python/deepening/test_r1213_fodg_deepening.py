"""Sprint 659 FODG analytics deepening tests - primes 1531, 1543."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1531_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1531_times_14200_plus_shape_times_391_plus_text_times_388_plus_page_times_394
    assert fodg_file_size_mod_1531_times_14200_plus_shape_times_391_plus_text_times_388_plus_page_times_394(str(EMPTY)) == 14952994


def test_mod1531_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1531_times_14200_plus_shape_times_391_plus_text_times_388_plus_page_times_394
    assert fodg_file_size_mod_1531_times_14200_plus_shape_times_391_plus_text_times_388_plus_page_times_394(str(MINIMAL)) == 20917773


def test_mod1531_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1531_times_14200_plus_shape_times_391_plus_text_times_388_plus_page_times_394
    assert fodg_file_size_mod_1531_times_14200_plus_shape_times_391_plus_text_times_388_plus_page_times_394(str(SHAPES)) == 1379743


def test_mod1543_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1543_times_14300_plus_shape_times_393_plus_text_times_390_plus_page_times_396
    assert fodg_file_size_mod_1543_times_14300_plus_shape_times_393_plus_text_times_390_plus_page_times_396(str(EMPTY)) == 15058296


def test_mod1543_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1543_times_14300_plus_shape_times_393_plus_text_times_390_plus_page_times_396
    assert fodg_file_size_mod_1543_times_14300_plus_shape_times_393_plus_text_times_390_plus_page_times_396(str(MINIMAL)) == 21065079


def test_mod1543_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1543_times_14300_plus_shape_times_393_plus_text_times_390_plus_page_times_396
    assert fodg_file_size_mod_1543_times_14300_plus_shape_times_393_plus_text_times_390_plus_page_times_396(str(SHAPES)) == 1217855


def test_mod1531_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1531_times_14200_plus_shape_times_391_plus_text_times_388_plus_page_times_394
    assert isinstance(fodg_file_size_mod_1531_times_14200_plus_shape_times_391_plus_text_times_388_plus_page_times_394(str(EMPTY)), int)


def test_mod1543_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1543_times_14300_plus_shape_times_393_plus_text_times_390_plus_page_times_396
    assert isinstance(fodg_file_size_mod_1543_times_14300_plus_shape_times_393_plus_text_times_390_plus_page_times_396(str(EMPTY)), int)


def test_mod1531_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1531_times_14200_plus_shape_times_391_plus_text_times_388_plus_page_times_394
    assert fodg_file_size_mod_1531_times_14200_plus_shape_times_391_plus_text_times_388_plus_page_times_394(str(EMPTY)) >= 0


def test_mod1543_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1543_times_14300_plus_shape_times_393_plus_text_times_390_plus_page_times_396
    assert fodg_file_size_mod_1543_times_14300_plus_shape_times_393_plus_text_times_390_plus_page_times_396(str(EMPTY)) >= 0


def test_mod1531_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1531_times_14200_plus_shape_times_391_plus_text_times_388_plus_page_times_394
    fn = fodg_file_size_mod_1531_times_14200_plus_shape_times_391_plus_text_times_388_plus_page_times_394
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1543_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1543_times_14300_plus_shape_times_393_plus_text_times_390_plus_page_times_396
    fn = fodg_file_size_mod_1543_times_14300_plus_shape_times_393_plus_text_times_390_plus_page_times_396
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1531_importable_from_package():
    from fodg import fodg_file_size_mod_1531_times_14200_plus_shape_times_391_plus_text_times_388_plus_page_times_394
    assert callable(fodg_file_size_mod_1531_times_14200_plus_shape_times_391_plus_text_times_388_plus_page_times_394)


def test_mod1543_importable_from_package():
    from fodg import fodg_file_size_mod_1543_times_14300_plus_shape_times_393_plus_text_times_390_plus_page_times_396
    assert callable(fodg_file_size_mod_1543_times_14300_plus_shape_times_393_plus_text_times_390_plus_page_times_396)
