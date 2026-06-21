"""Sprint 626 FODG analytics deepening tests - primes 1373, 1381."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1373_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1373_times_12000_plus_shape_times_347_plus_text_times_344_plus_page_times_350
    assert fodg_file_size_mod_1373_times_12000_plus_shape_times_347_plus_text_times_344_plus_page_times_350(str(EMPTY)) == 12636350


def test_mod1373_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1373_times_12000_plus_shape_times_347_plus_text_times_344_plus_page_times_350
    assert fodg_file_size_mod_1373_times_12000_plus_shape_times_347_plus_text_times_344_plus_page_times_350(str(MINIMAL)) == 1201041


def test_mod1373_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1373_times_12000_plus_shape_times_347_plus_text_times_344_plus_page_times_350
    assert fodg_file_size_mod_1373_times_12000_plus_shape_times_347_plus_text_times_344_plus_page_times_350(str(SHAPES)) == 3062079


def test_mod1381_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1381_times_12100_plus_shape_times_349_plus_text_times_346_plus_page_times_352
    assert fodg_file_size_mod_1381_times_12100_plus_shape_times_349_plus_text_times_346_plus_page_times_352(str(EMPTY)) == 12741652


def test_mod1381_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1381_times_12100_plus_shape_times_349_plus_text_times_346_plus_page_times_352
    assert fodg_file_size_mod_1381_times_12100_plus_shape_times_349_plus_text_times_346_plus_page_times_352(str(MINIMAL)) == 1114247


def test_mod1381_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1381_times_12100_plus_shape_times_349_plus_text_times_346_plus_page_times_352
    assert fodg_file_size_mod_1381_times_12100_plus_shape_times_349_plus_text_times_346_plus_page_times_352(str(SHAPES)) == 2990791


def test_mod1373_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1373_times_12000_plus_shape_times_347_plus_text_times_344_plus_page_times_350
    assert isinstance(fodg_file_size_mod_1373_times_12000_plus_shape_times_347_plus_text_times_344_plus_page_times_350(str(EMPTY)), int)


def test_mod1381_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1381_times_12100_plus_shape_times_349_plus_text_times_346_plus_page_times_352
    assert isinstance(fodg_file_size_mod_1381_times_12100_plus_shape_times_349_plus_text_times_346_plus_page_times_352(str(EMPTY)), int)


def test_mod1373_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1373_times_12000_plus_shape_times_347_plus_text_times_344_plus_page_times_350
    assert fodg_file_size_mod_1373_times_12000_plus_shape_times_347_plus_text_times_344_plus_page_times_350(str(EMPTY)) >= 0


def test_mod1381_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1381_times_12100_plus_shape_times_349_plus_text_times_346_plus_page_times_352
    assert fodg_file_size_mod_1381_times_12100_plus_shape_times_349_plus_text_times_346_plus_page_times_352(str(EMPTY)) >= 0


def test_mod1373_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1373_times_12000_plus_shape_times_347_plus_text_times_344_plus_page_times_350
    fn = fodg_file_size_mod_1373_times_12000_plus_shape_times_347_plus_text_times_344_plus_page_times_350
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1381_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1381_times_12100_plus_shape_times_349_plus_text_times_346_plus_page_times_352
    fn = fodg_file_size_mod_1381_times_12100_plus_shape_times_349_plus_text_times_346_plus_page_times_352
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1373_importable_from_package():
    from fodg import fodg_file_size_mod_1373_times_12000_plus_shape_times_347_plus_text_times_344_plus_page_times_350
    assert callable(fodg_file_size_mod_1373_times_12000_plus_shape_times_347_plus_text_times_344_plus_page_times_350)


def test_mod1381_importable_from_package():
    from fodg import fodg_file_size_mod_1381_times_12100_plus_shape_times_349_plus_text_times_346_plus_page_times_352
    assert callable(fodg_file_size_mod_1381_times_12100_plus_shape_times_349_plus_text_times_346_plus_page_times_352)
