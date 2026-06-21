"""Sprint 620 FODG analytics deepening tests - primes 1321, 1327."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"


def test_mod1321_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1321_times_11600_plus_shape_times_339_plus_text_times_336_plus_page_times_342
    assert fodg_file_size_mod_1321_times_11600_plus_shape_times_339_plus_text_times_336_plus_page_times_342(str(EMPTY)) == 12215142

def test_mod1321_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1321_times_11600_plus_shape_times_339_plus_text_times_336_plus_page_times_342
    assert fodg_file_size_mod_1321_times_11600_plus_shape_times_339_plus_text_times_336_plus_page_times_342(str(MINIMAL)) == 1764217

def test_mod1321_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1321_times_11600_plus_shape_times_339_plus_text_times_336_plus_page_times_342
    assert fodg_file_size_mod_1321_times_11600_plus_shape_times_339_plus_text_times_336_plus_page_times_342(str(SHAPES)) == 3563231

def test_mod1327_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1327_times_11700_plus_shape_times_341_plus_text_times_338_plus_page_times_344
    assert fodg_file_size_mod_1327_times_11700_plus_shape_times_341_plus_text_times_338_plus_page_times_344(str(EMPTY)) == 12320444

def test_mod1327_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1327_times_11700_plus_shape_times_341_plus_text_times_338_plus_page_times_344
    assert fodg_file_size_mod_1327_times_11700_plus_shape_times_341_plus_text_times_338_plus_page_times_344(str(MINIMAL)) == 1709223

def test_mod1327_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1327_times_11700_plus_shape_times_341_plus_text_times_338_plus_page_times_344
    assert fodg_file_size_mod_1327_times_11700_plus_shape_times_341_plus_text_times_338_plus_page_times_344(str(SHAPES)) == 3523743

def test_mod1321_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1321_times_11600_plus_shape_times_339_plus_text_times_336_plus_page_times_342
    assert isinstance(fodg_file_size_mod_1321_times_11600_plus_shape_times_339_plus_text_times_336_plus_page_times_342(str(EMPTY)), int)

def test_mod1327_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1327_times_11700_plus_shape_times_341_plus_text_times_338_plus_page_times_344
    assert isinstance(fodg_file_size_mod_1327_times_11700_plus_shape_times_341_plus_text_times_338_plus_page_times_344(str(EMPTY)), int)

def test_mod1321_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1321_times_11600_plus_shape_times_339_plus_text_times_336_plus_page_times_342
    assert fodg_file_size_mod_1321_times_11600_plus_shape_times_339_plus_text_times_336_plus_page_times_342(str(EMPTY)) >= 0

def test_mod1327_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1327_times_11700_plus_shape_times_341_plus_text_times_338_plus_page_times_344
    assert fodg_file_size_mod_1327_times_11700_plus_shape_times_341_plus_text_times_338_plus_page_times_344(str(EMPTY)) >= 0

def test_mod1321_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1321_times_11600_plus_shape_times_339_plus_text_times_336_plus_page_times_342
    fn = fodg_file_size_mod_1321_times_11600_plus_shape_times_339_plus_text_times_336_plus_page_times_342
    assert len({fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}) == 3

def test_mod1327_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1327_times_11700_plus_shape_times_341_plus_text_times_338_plus_page_times_344
    fn = fodg_file_size_mod_1327_times_11700_plus_shape_times_341_plus_text_times_338_plus_page_times_344
    assert len({fn(str(EMPTY)), fn(str(MINIMAL)), fn(str(SHAPES))}) == 3

def test_mod1321_importable_from_package():
    from fodg import fodg_file_size_mod_1321_times_11600_plus_shape_times_339_plus_text_times_336_plus_page_times_342
    assert callable(fodg_file_size_mod_1321_times_11600_plus_shape_times_339_plus_text_times_336_plus_page_times_342)

def test_mod1327_importable_from_package():
    from fodg import fodg_file_size_mod_1327_times_11700_plus_shape_times_341_plus_text_times_338_plus_page_times_344
    assert callable(fodg_file_size_mod_1327_times_11700_plus_shape_times_341_plus_text_times_338_plus_page_times_344)
