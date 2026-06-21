"""Sprint 635 FODG analytics deepening tests - primes 1429, 1433."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1429_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1429_times_12600_plus_shape_times_359_plus_text_times_356_plus_page_times_362
    assert fodg_file_size_mod_1429_times_12600_plus_shape_times_359_plus_text_times_356_plus_page_times_362(str(EMPTY)) == 13268162


def test_mod1429_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1429_times_12600_plus_shape_times_359_plus_text_times_356_plus_page_times_362
    assert fodg_file_size_mod_1429_times_12600_plus_shape_times_359_plus_text_times_356_plus_page_times_362(str(MINIMAL)) == 555477


def test_mod1429_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1429_times_12600_plus_shape_times_359_plus_text_times_356_plus_page_times_362
    assert fodg_file_size_mod_1429_times_12600_plus_shape_times_359_plus_text_times_356_plus_page_times_362(str(SHAPES)) == 2509551


def test_mod1429_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1429_times_12600_plus_shape_times_359_plus_text_times_356_plus_page_times_362
    assert isinstance(fodg_file_size_mod_1429_times_12600_plus_shape_times_359_plus_text_times_356_plus_page_times_362(str(EMPTY)), int)


def test_mod1429_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1429_times_12600_plus_shape_times_359_plus_text_times_356_plus_page_times_362
    assert fodg_file_size_mod_1429_times_12600_plus_shape_times_359_plus_text_times_356_plus_page_times_362(str(EMPTY)) >= 0


def test_mod1429_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1429_times_12600_plus_shape_times_359_plus_text_times_356_plus_page_times_362
    fn_ref = fodg_file_size_mod_1429_times_12600_plus_shape_times_359_plus_text_times_356_plus_page_times_362
    results = {fn_ref(str(EMPTY)), fn_ref(str(MINIMAL)), fn_ref(str(SHAPES))}
    assert len(results) == 3


def test_mod1429_importable_from_package():
    from fodg import fodg_file_size_mod_1429_times_12600_plus_shape_times_359_plus_text_times_356_plus_page_times_362
    assert callable(fodg_file_size_mod_1429_times_12600_plus_shape_times_359_plus_text_times_356_plus_page_times_362)


def test_mod1433_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1433_times_12700_plus_shape_times_361_plus_text_times_358_plus_page_times_364
    assert fodg_file_size_mod_1433_times_12700_plus_shape_times_361_plus_text_times_358_plus_page_times_364(str(EMPTY)) == 13373464


def test_mod1433_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1433_times_12700_plus_shape_times_361_plus_text_times_358_plus_page_times_364
    assert fodg_file_size_mod_1433_times_12700_plus_shape_times_361_plus_text_times_358_plus_page_times_364(str(MINIMAL)) == 509083


def test_mod1433_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1433_times_12700_plus_shape_times_361_plus_text_times_358_plus_page_times_364
    assert fodg_file_size_mod_1433_times_12700_plus_shape_times_361_plus_text_times_358_plus_page_times_364(str(SHAPES)) == 2478663


def test_mod1433_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1433_times_12700_plus_shape_times_361_plus_text_times_358_plus_page_times_364
    assert isinstance(fodg_file_size_mod_1433_times_12700_plus_shape_times_361_plus_text_times_358_plus_page_times_364(str(EMPTY)), int)


def test_mod1433_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1433_times_12700_plus_shape_times_361_plus_text_times_358_plus_page_times_364
    assert fodg_file_size_mod_1433_times_12700_plus_shape_times_361_plus_text_times_358_plus_page_times_364(str(EMPTY)) >= 0


def test_mod1433_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1433_times_12700_plus_shape_times_361_plus_text_times_358_plus_page_times_364
    fn_ref = fodg_file_size_mod_1433_times_12700_plus_shape_times_361_plus_text_times_358_plus_page_times_364
    results = {fn_ref(str(EMPTY)), fn_ref(str(MINIMAL)), fn_ref(str(SHAPES))}
    assert len(results) == 3


def test_mod1433_importable_from_package():
    from fodg import fodg_file_size_mod_1433_times_12700_plus_shape_times_361_plus_text_times_358_plus_page_times_364
    assert callable(fodg_file_size_mod_1433_times_12700_plus_shape_times_361_plus_text_times_358_plus_page_times_364)
