"""Sprint 563 FODG analytics deepening tests - primes 1061, 1063."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1061_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1061_times_7800_plus_shape_times_263_plus_text_times_260_plus_page_times_266
    assert fodg_file_size_mod_1061_times_7800_plus_shape_times_263_plus_text_times_260_plus_page_times_266(str(EMPTY)) == 8213666


def test_mod1061_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1061_times_7800_plus_shape_times_263_plus_text_times_260_plus_page_times_266
    assert fodg_file_size_mod_1061_times_7800_plus_shape_times_263_plus_text_times_260_plus_page_times_266(str(MINIMAL)) == 3214389


def test_mod1061_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1061_times_7800_plus_shape_times_263_plus_text_times_260_plus_page_times_266
    assert fodg_file_size_mod_1061_times_7800_plus_shape_times_263_plus_text_times_260_plus_page_times_266(str(SHAPES)) == 4424175


def test_mod1063_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1063_times_7900_plus_shape_times_265_plus_text_times_262_plus_page_times_268
    assert fodg_file_size_mod_1063_times_7900_plus_shape_times_265_plus_text_times_262_plus_page_times_268(str(EMPTY)) == 8318968


def test_mod1063_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1063_times_7900_plus_shape_times_265_plus_text_times_262_plus_page_times_268
    assert fodg_file_size_mod_1063_times_7900_plus_shape_times_265_plus_text_times_262_plus_page_times_268(str(MINIMAL)) == 3239795


def test_mod1063_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1063_times_7900_plus_shape_times_265_plus_text_times_262_plus_page_times_268
    assert fodg_file_size_mod_1063_times_7900_plus_shape_times_265_plus_text_times_262_plus_page_times_268(str(SHAPES)) == 4465087


def test_mod1061_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1061_times_7800_plus_shape_times_263_plus_text_times_260_plus_page_times_266
    assert isinstance(fodg_file_size_mod_1061_times_7800_plus_shape_times_263_plus_text_times_260_plus_page_times_266(str(EMPTY)), int)


def test_mod1063_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1063_times_7900_plus_shape_times_265_plus_text_times_262_plus_page_times_268
    assert isinstance(fodg_file_size_mod_1063_times_7900_plus_shape_times_265_plus_text_times_262_plus_page_times_268(str(EMPTY)), int)


def test_mod1061_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1061_times_7800_plus_shape_times_263_plus_text_times_260_plus_page_times_266
    assert fodg_file_size_mod_1061_times_7800_plus_shape_times_263_plus_text_times_260_plus_page_times_266(str(EMPTY)) >= 0


def test_mod1063_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1063_times_7900_plus_shape_times_265_plus_text_times_262_plus_page_times_268
    assert fodg_file_size_mod_1063_times_7900_plus_shape_times_265_plus_text_times_262_plus_page_times_268(str(EMPTY)) >= 0


def test_mod1061_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1061_times_7800_plus_shape_times_263_plus_text_times_260_plus_page_times_266
    fn = fodg_file_size_mod_1061_times_7800_plus_shape_times_263_plus_text_times_260_plus_page_times_266
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1063_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1063_times_7900_plus_shape_times_265_plus_text_times_262_plus_page_times_268
    fn = fodg_file_size_mod_1063_times_7900_plus_shape_times_265_plus_text_times_262_plus_page_times_268
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1061_importable_from_package():
    from fodg import fodg_file_size_mod_1061_times_7800_plus_shape_times_263_plus_text_times_260_plus_page_times_266
    assert callable(fodg_file_size_mod_1061_times_7800_plus_shape_times_263_plus_text_times_260_plus_page_times_266)


def test_mod1063_importable_from_package():
    from fodg import fodg_file_size_mod_1063_times_7900_plus_shape_times_265_plus_text_times_262_plus_page_times_268
    assert callable(fodg_file_size_mod_1063_times_7900_plus_shape_times_265_plus_text_times_262_plus_page_times_268)
