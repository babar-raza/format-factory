"""Sprint 629 FODG analytics deepening tests - primes 1399, 1409."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1399_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1399_times_12200_plus_shape_times_351_plus_text_times_348_plus_page_times_354
    assert fodg_file_size_mod_1399_times_12200_plus_shape_times_351_plus_text_times_348_plus_page_times_354(str(EMPTY)) == 12846954


def test_mod1399_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1399_times_12200_plus_shape_times_351_plus_text_times_348_plus_page_times_354
    assert fodg_file_size_mod_1399_times_12200_plus_shape_times_351_plus_text_times_348_plus_page_times_354(str(MINIMAL)) == 903853


def test_mod1399_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1399_times_12200_plus_shape_times_351_plus_text_times_348_plus_page_times_354
    assert fodg_file_size_mod_1399_times_12200_plus_shape_times_351_plus_text_times_348_plus_page_times_354(str(SHAPES)) == 2795903


def test_mod1409_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1409_times_12300_plus_shape_times_353_plus_text_times_350_plus_page_times_356
    assert fodg_file_size_mod_1409_times_12300_plus_shape_times_353_plus_text_times_350_plus_page_times_356(str(EMPTY)) == 12952256


def test_mod1409_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1409_times_12300_plus_shape_times_353_plus_text_times_350_plus_page_times_356
    assert fodg_file_size_mod_1409_times_12300_plus_shape_times_353_plus_text_times_350_plus_page_times_356(str(MINIMAL)) == 788259


def test_mod1409_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1409_times_12300_plus_shape_times_353_plus_text_times_350_plus_page_times_356
    assert fodg_file_size_mod_1409_times_12300_plus_shape_times_353_plus_text_times_350_plus_page_times_356(str(SHAPES)) == 2695815


def test_mod1399_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1399_times_12200_plus_shape_times_351_plus_text_times_348_plus_page_times_354
    assert isinstance(fodg_file_size_mod_1399_times_12200_plus_shape_times_351_plus_text_times_348_plus_page_times_354(str(EMPTY)), int)


def test_mod1409_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1409_times_12300_plus_shape_times_353_plus_text_times_350_plus_page_times_356
    assert isinstance(fodg_file_size_mod_1409_times_12300_plus_shape_times_353_plus_text_times_350_plus_page_times_356(str(EMPTY)), int)


def test_mod1399_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1399_times_12200_plus_shape_times_351_plus_text_times_348_plus_page_times_354
    assert fodg_file_size_mod_1399_times_12200_plus_shape_times_351_plus_text_times_348_plus_page_times_354(str(EMPTY)) >= 0


def test_mod1409_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1409_times_12300_plus_shape_times_353_plus_text_times_350_plus_page_times_356
    assert fodg_file_size_mod_1409_times_12300_plus_shape_times_353_plus_text_times_350_plus_page_times_356(str(EMPTY)) >= 0


def test_mod1399_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1399_times_12200_plus_shape_times_351_plus_text_times_348_plus_page_times_354
    fn = fodg_file_size_mod_1399_times_12200_plus_shape_times_351_plus_text_times_348_plus_page_times_354
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1409_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1409_times_12300_plus_shape_times_353_plus_text_times_350_plus_page_times_356
    fn = fodg_file_size_mod_1409_times_12300_plus_shape_times_353_plus_text_times_350_plus_page_times_356
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1399_importable_from_package():
    from fodg import fodg_file_size_mod_1399_times_12200_plus_shape_times_351_plus_text_times_348_plus_page_times_354
    assert callable(fodg_file_size_mod_1399_times_12200_plus_shape_times_351_plus_text_times_348_plus_page_times_354)


def test_mod1409_importable_from_package():
    from fodg import fodg_file_size_mod_1409_times_12300_plus_shape_times_353_plus_text_times_350_plus_page_times_356
    assert callable(fodg_file_size_mod_1409_times_12300_plus_shape_times_353_plus_text_times_350_plus_page_times_356)
