"""Sprint 602 FODG analytics deepening tests - primes 1249, 1259."""
from pathlib import Path

SAMPLES = Path("samples/by-format/fodg")
EMPTY = SAMPLES / "empty-page.fodg"
MINIMAL = SAMPLES / "minimal-drawing.fodg"
SHAPES = SAMPLES / "shapes-basic.fodg"

def test_mod1249_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1249_times_10400_plus_shape_times_315_plus_text_times_312_plus_page_times_318
    assert fodg_file_size_mod_1249_times_10400_plus_shape_times_315_plus_text_times_312_plus_page_times_318(str(EMPTY)) == 10951518

def test_mod1249_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1249_times_10400_plus_shape_times_315_plus_text_times_312_plus_page_times_318
    assert fodg_file_size_mod_1249_times_10400_plus_shape_times_315_plus_text_times_312_plus_page_times_318(str(MINIMAL)) == 2330545

def test_mod1249_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1249_times_10400_plus_shape_times_315_plus_text_times_312_plus_page_times_318
    assert fodg_file_size_mod_1249_times_10400_plus_shape_times_315_plus_text_times_312_plus_page_times_318(str(SHAPES)) == 3943487

def test_mod1259_empty():
    from fodg.fodg_analytics import fodg_file_size_mod_1259_times_10500_plus_shape_times_317_plus_text_times_314_plus_page_times_320
    assert fodg_file_size_mod_1259_times_10500_plus_shape_times_317_plus_text_times_314_plus_page_times_320(str(EMPTY)) == 11056820

def test_mod1259_minimal():
    from fodg.fodg_analytics import fodg_file_size_mod_1259_times_10500_plus_shape_times_317_plus_text_times_314_plus_page_times_320
    assert fodg_file_size_mod_1259_times_10500_plus_shape_times_317_plus_text_times_314_plus_page_times_320(str(MINIMAL)) == 2247951

def test_mod1259_shapes():
    from fodg.fodg_analytics import fodg_file_size_mod_1259_times_10500_plus_shape_times_317_plus_text_times_314_plus_page_times_320
    assert fodg_file_size_mod_1259_times_10500_plus_shape_times_317_plus_text_times_314_plus_page_times_320(str(SHAPES)) == 3876399

def test_mod1249_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1249_times_10400_plus_shape_times_315_plus_text_times_312_plus_page_times_318
    assert isinstance(fodg_file_size_mod_1249_times_10400_plus_shape_times_315_plus_text_times_312_plus_page_times_318(str(EMPTY)), int)

def test_mod1249_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1249_times_10400_plus_shape_times_315_plus_text_times_312_plus_page_times_318
    assert fodg_file_size_mod_1249_times_10400_plus_shape_times_315_plus_text_times_312_plus_page_times_318(str(EMPTY)) >= 0

def test_mod1249_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1249_times_10400_plus_shape_times_315_plus_text_times_312_plus_page_times_318
    fn2 = fodg_file_size_mod_1249_times_10400_plus_shape_times_315_plus_text_times_312_plus_page_times_318
    results = {fn2(str(EMPTY)), fn2(str(MINIMAL)), fn2(str(SHAPES))}
    assert len(results) == 3

def test_mod1249_importable_from_package():
    from fodg import fodg_file_size_mod_1249_times_10400_plus_shape_times_315_plus_text_times_312_plus_page_times_318
    assert callable(fodg_file_size_mod_1249_times_10400_plus_shape_times_315_plus_text_times_312_plus_page_times_318)

def test_mod1259_returns_int():
    from fodg.fodg_analytics import fodg_file_size_mod_1259_times_10500_plus_shape_times_317_plus_text_times_314_plus_page_times_320
    assert isinstance(fodg_file_size_mod_1259_times_10500_plus_shape_times_317_plus_text_times_314_plus_page_times_320(str(EMPTY)), int)

def test_mod1259_nonnegative():
    from fodg.fodg_analytics import fodg_file_size_mod_1259_times_10500_plus_shape_times_317_plus_text_times_314_plus_page_times_320
    assert fodg_file_size_mod_1259_times_10500_plus_shape_times_317_plus_text_times_314_plus_page_times_320(str(EMPTY)) >= 0

def test_mod1259_all_samples_differ():
    from fodg.fodg_analytics import fodg_file_size_mod_1259_times_10500_plus_shape_times_317_plus_text_times_314_plus_page_times_320
    fn2 = fodg_file_size_mod_1259_times_10500_plus_shape_times_317_plus_text_times_314_plus_page_times_320
    results = {fn2(str(EMPTY)), fn2(str(MINIMAL)), fn2(str(SHAPES))}
    assert len(results) == 3

def test_mod1259_importable_from_package():
    from fodg import fodg_file_size_mod_1259_times_10500_plus_shape_times_317_plus_text_times_314_plus_page_times_320
    assert callable(fodg_file_size_mod_1259_times_10500_plus_shape_times_317_plus_text_times_314_plus_page_times_320)
