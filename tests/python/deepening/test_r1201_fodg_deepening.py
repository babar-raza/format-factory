"""Sprint 647 FODG analytics deepening tests - primes 1481, 1483."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1481_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1481_times_13400_plus_shape_times_375_plus_text_times_372_plus_page_times_378
    assert fodg_file_size_mod_1481_times_13400_plus_shape_times_375_plus_text_times_372_plus_page_times_378(str(EMPTY)) == 14110578


def test_mod1481_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1481_times_13400_plus_shape_times_375_plus_text_times_372_plus_page_times_378
    assert fodg_file_size_mod_1481_times_13400_plus_shape_times_375_plus_text_times_372_plus_page_times_378(str(MINIMAL)) == 19739325


def test_mod1481_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1481_times_13400_plus_shape_times_375_plus_text_times_372_plus_page_times_378
    assert fodg_file_size_mod_1481_times_13400_plus_shape_times_375_plus_text_times_372_plus_page_times_378(str(SHAPES)) == 1972047


def test_mod1483_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1483_times_13500_plus_shape_times_377_plus_text_times_374_plus_page_times_380
    assert fodg_file_size_mod_1483_times_13500_plus_shape_times_377_plus_text_times_374_plus_page_times_380(str(EMPTY)) == 14215880


def test_mod1483_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1483_times_13500_plus_shape_times_377_plus_text_times_374_plus_page_times_380
    assert fodg_file_size_mod_1483_times_13500_plus_shape_times_377_plus_text_times_374_plus_page_times_380(str(MINIMAL)) == 19886631


def test_mod1483_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1483_times_13500_plus_shape_times_377_plus_text_times_374_plus_page_times_380
    assert fodg_file_size_mod_1483_times_13500_plus_shape_times_377_plus_text_times_374_plus_page_times_380(str(SHAPES)) == 1959759


def test_mod1481_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1481_times_13400_plus_shape_times_375_plus_text_times_372_plus_page_times_378
    assert isinstance(fodg_file_size_mod_1481_times_13400_plus_shape_times_375_plus_text_times_372_plus_page_times_378(str(EMPTY)), int)


def test_mod1483_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1483_times_13500_plus_shape_times_377_plus_text_times_374_plus_page_times_380
    assert isinstance(fodg_file_size_mod_1483_times_13500_plus_shape_times_377_plus_text_times_374_plus_page_times_380(str(EMPTY)), int)


def test_mod1481_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1481_times_13400_plus_shape_times_375_plus_text_times_372_plus_page_times_378
    assert fodg_file_size_mod_1481_times_13400_plus_shape_times_375_plus_text_times_372_plus_page_times_378(str(EMPTY)) >= 0


def test_mod1483_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1483_times_13500_plus_shape_times_377_plus_text_times_374_plus_page_times_380
    assert fodg_file_size_mod_1483_times_13500_plus_shape_times_377_plus_text_times_374_plus_page_times_380(str(EMPTY)) >= 0


def test_mod1481_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1481_times_13400_plus_shape_times_375_plus_text_times_372_plus_page_times_378
    fn = fodg_file_size_mod_1481_times_13400_plus_shape_times_375_plus_text_times_372_plus_page_times_378
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1483_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1483_times_13500_plus_shape_times_377_plus_text_times_374_plus_page_times_380
    fn = fodg_file_size_mod_1483_times_13500_plus_shape_times_377_plus_text_times_374_plus_page_times_380
    results = {fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}
    assert len(results) == 3


def test_mod1481_importable_from_package():
    from fodg import fodg_file_size_mod_1481_times_13400_plus_shape_times_375_plus_text_times_372_plus_page_times_378
    assert callable(fodg_file_size_mod_1481_times_13400_plus_shape_times_375_plus_text_times_372_plus_page_times_378)


def test_mod1483_importable_from_package():
    from fodg import fodg_file_size_mod_1483_times_13500_plus_shape_times_377_plus_text_times_374_plus_page_times_380
    assert callable(fodg_file_size_mod_1483_times_13500_plus_shape_times_377_plus_text_times_374_plus_page_times_380)
