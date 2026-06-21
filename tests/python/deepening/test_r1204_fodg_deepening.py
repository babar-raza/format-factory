"""Sprint 650 FODG analytics deepening tests - primes 1487, 1489."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1487_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1487_times_13600_plus_shape_times_379_plus_text_times_376_plus_page_times_382
    assert fodg_file_size_mod_1487_times_13600_plus_shape_times_379_plus_text_times_376_plus_page_times_382(str(EMPTY)) == 14321182


def test_mod1487_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1487_times_13600_plus_shape_times_379_plus_text_times_376_plus_page_times_382
    assert fodg_file_size_mod_1487_times_13600_plus_shape_times_379_plus_text_times_376_plus_page_times_382(str(MINIMAL)) == 20033937


def test_mod1487_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1487_times_13600_plus_shape_times_379_plus_text_times_376_plus_page_times_382
    assert fodg_file_size_mod_1487_times_13600_plus_shape_times_379_plus_text_times_376_plus_page_times_382(str(SHAPES)) == 1919871


def test_mod1489_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1489_times_13700_plus_shape_times_381_plus_text_times_378_plus_page_times_384
    assert fodg_file_size_mod_1489_times_13700_plus_shape_times_381_plus_text_times_378_plus_page_times_384(str(EMPTY)) == 14426484


def test_mod1489_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1489_times_13700_plus_shape_times_381_plus_text_times_378_plus_page_times_384
    assert fodg_file_size_mod_1489_times_13700_plus_shape_times_381_plus_text_times_378_plus_page_times_384(str(MINIMAL)) == 20181243


def test_mod1489_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1489_times_13700_plus_shape_times_381_plus_text_times_378_plus_page_times_384
    assert fodg_file_size_mod_1489_times_13700_plus_shape_times_381_plus_text_times_378_plus_page_times_384(str(SHAPES)) == 1906583


def test_mod1487_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1487_times_13600_plus_shape_times_379_plus_text_times_376_plus_page_times_382
    assert isinstance(fodg_file_size_mod_1487_times_13600_plus_shape_times_379_plus_text_times_376_plus_page_times_382(str(EMPTY)), int)


def test_mod1489_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1489_times_13700_plus_shape_times_381_plus_text_times_378_plus_page_times_384
    assert isinstance(fodg_file_size_mod_1489_times_13700_plus_shape_times_381_plus_text_times_378_plus_page_times_384(str(EMPTY)), int)


def test_mod1487_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1487_times_13600_plus_shape_times_379_plus_text_times_376_plus_page_times_382
    assert fodg_file_size_mod_1487_times_13600_plus_shape_times_379_plus_text_times_376_plus_page_times_382(str(EMPTY)) >= 0


def test_mod1489_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1489_times_13700_plus_shape_times_381_plus_text_times_378_plus_page_times_384
    assert fodg_file_size_mod_1489_times_13700_plus_shape_times_381_plus_text_times_378_plus_page_times_384(str(EMPTY)) >= 0


def test_mod1487_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1487_times_13600_plus_shape_times_379_plus_text_times_376_plus_page_times_382
    fn = fodg_file_size_mod_1487_times_13600_plus_shape_times_379_plus_text_times_376_plus_page_times_382
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1489_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1489_times_13700_plus_shape_times_381_plus_text_times_378_plus_page_times_384
    fn = fodg_file_size_mod_1489_times_13700_plus_shape_times_381_plus_text_times_378_plus_page_times_384
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1487_importable_from_package():
    from fodg import fodg_file_size_mod_1487_times_13600_plus_shape_times_379_plus_text_times_376_plus_page_times_382
    assert callable(fodg_file_size_mod_1487_times_13600_plus_shape_times_379_plus_text_times_376_plus_page_times_382)


def test_mod1489_importable_from_package():
    from fodg import fodg_file_size_mod_1489_times_13700_plus_shape_times_381_plus_text_times_378_plus_page_times_384
    assert callable(fodg_file_size_mod_1489_times_13700_plus_shape_times_381_plus_text_times_378_plus_page_times_384)
