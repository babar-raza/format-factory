"""Sprint 656 FODG analytics deepening tests - primes 1511, 1523."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1511_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1511_times_14000_plus_shape_times_387_plus_text_times_384_plus_page_times_390
    assert fodg_file_size_mod_1511_times_14000_plus_shape_times_387_plus_text_times_384_plus_page_times_390(str(EMPTY)) == 14742390


def test_mod1511_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1511_times_14000_plus_shape_times_387_plus_text_times_384_plus_page_times_390
    assert fodg_file_size_mod_1511_times_14000_plus_shape_times_387_plus_text_times_384_plus_page_times_390(str(MINIMAL)) == 20623161


def test_mod1511_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1511_times_14000_plus_shape_times_387_plus_text_times_384_plus_page_times_390
    assert fodg_file_size_mod_1511_times_14000_plus_shape_times_387_plus_text_times_384_plus_page_times_390(str(SHAPES)) == 1640319


def test_mod1523_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1523_times_14100_plus_shape_times_389_plus_text_times_386_plus_page_times_392
    assert fodg_file_size_mod_1523_times_14100_plus_shape_times_389_plus_text_times_386_plus_page_times_392(str(EMPTY)) == 14847692


def test_mod1523_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1523_times_14100_plus_shape_times_389_plus_text_times_386_plus_page_times_392
    assert fodg_file_size_mod_1523_times_14100_plus_shape_times_389_plus_text_times_386_plus_page_times_392(str(MINIMAL)) == 20770467


def test_mod1523_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1523_times_14100_plus_shape_times_389_plus_text_times_386_plus_page_times_392
    assert fodg_file_size_mod_1523_times_14100_plus_shape_times_389_plus_text_times_386_plus_page_times_392(str(SHAPES)) == 1482831


def test_mod1511_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1511_times_14000_plus_shape_times_387_plus_text_times_384_plus_page_times_390
    assert isinstance(fodg_file_size_mod_1511_times_14000_plus_shape_times_387_plus_text_times_384_plus_page_times_390(str(EMPTY)), int)


def test_mod1523_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1523_times_14100_plus_shape_times_389_plus_text_times_386_plus_page_times_392
    assert isinstance(fodg_file_size_mod_1523_times_14100_plus_shape_times_389_plus_text_times_386_plus_page_times_392(str(EMPTY)), int)


def test_mod1511_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1511_times_14000_plus_shape_times_387_plus_text_times_384_plus_page_times_390
    assert fodg_file_size_mod_1511_times_14000_plus_shape_times_387_plus_text_times_384_plus_page_times_390(str(EMPTY)) >= 0


def test_mod1523_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1523_times_14100_plus_shape_times_389_plus_text_times_386_plus_page_times_392
    assert fodg_file_size_mod_1523_times_14100_plus_shape_times_389_plus_text_times_386_plus_page_times_392(str(EMPTY)) >= 0


def test_mod1511_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1511_times_14000_plus_shape_times_387_plus_text_times_384_plus_page_times_390
    fn = fodg_file_size_mod_1511_times_14000_plus_shape_times_387_plus_text_times_384_plus_page_times_390
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1523_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1523_times_14100_plus_shape_times_389_plus_text_times_386_plus_page_times_392
    fn = fodg_file_size_mod_1523_times_14100_plus_shape_times_389_plus_text_times_386_plus_page_times_392
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1511_importable_from_package():
    from fodg import fodg_file_size_mod_1511_times_14000_plus_shape_times_387_plus_text_times_384_plus_page_times_390
    assert callable(fodg_file_size_mod_1511_times_14000_plus_shape_times_387_plus_text_times_384_plus_page_times_390)


def test_mod1523_importable_from_package():
    from fodg import fodg_file_size_mod_1523_times_14100_plus_shape_times_389_plus_text_times_386_plus_page_times_392
    assert callable(fodg_file_size_mod_1523_times_14100_plus_shape_times_389_plus_text_times_386_plus_page_times_392)
