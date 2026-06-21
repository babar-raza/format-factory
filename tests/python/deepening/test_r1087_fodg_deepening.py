"""Tests for FODG analytics functions - sprint 533 (primes 929, 937)."""
from pathlib import Path
SAMPLES = {"empty": "samples/by-format/fodg/empty-page.fodg", "minimal": "samples/by-format/fodg/minimal-drawing.fodg", "shapes": "samples/by-format/fodg/shapes-basic.fodg"}
def test_fn1_empty():
    from fodg import fodg_file_size_mod_929_times_5800_plus_shape_times_223_plus_text_times_220_plus_page_times_226 as fn
    assert fn(SAMPLES["empty"]) == 719426
def test_fn1_minimal():
    from fodg import fodg_file_size_mod_929_times_5800_plus_shape_times_223_plus_text_times_220_plus_page_times_226 as fn
    assert fn(SAMPLES["minimal"]) == 3155869
def test_fn1_shapes():
    from fodg import fodg_file_size_mod_929_times_5800_plus_shape_times_223_plus_text_times_220_plus_page_times_226 as fn
    assert fn(SAMPLES["shapes"]) == 4055535
def test_fn1_int():
    from fodg import fodg_file_size_mod_929_times_5800_plus_shape_times_223_plus_text_times_220_plus_page_times_226 as fn
    assert isinstance(fn(SAMPLES["empty"]), int)
def test_fn1_nonneg():
    from fodg import fodg_file_size_mod_929_times_5800_plus_shape_times_223_plus_text_times_220_plus_page_times_226 as fn
    for s in SAMPLES.values(): assert fn(s) >= 0
def test_fn1_path():
    from fodg import fodg_file_size_mod_929_times_5800_plus_shape_times_223_plus_text_times_220_plus_page_times_226 as fn
    assert fn(Path(SAMPLES["empty"])) == 719426
def test_fn1_doc():
    from fodg import fodg_file_size_mod_929_times_5800_plus_shape_times_223_plus_text_times_220_plus_page_times_226 as fn
    assert fn.__doc__ is not None and "929" in fn.__doc__
def test_fn2_empty():
    from fodg import fodg_file_size_mod_937_times_5900_plus_shape_times_225_plus_text_times_222_plus_page_times_228 as fn
    assert fn(SAMPLES["empty"]) == 684628
def test_fn2_minimal():
    from fodg import fodg_file_size_mod_937_times_5900_plus_shape_times_225_plus_text_times_222_plus_page_times_228 as fn
    assert fn(SAMPLES["minimal"]) == 3163075
def test_fn2_shapes():
    from fodg import fodg_file_size_mod_937_times_5900_plus_shape_times_225_plus_text_times_222_plus_page_times_228 as fn
    assert fn(SAMPLES["shapes"]) == 4078247
def test_fn2_int():
    from fodg import fodg_file_size_mod_937_times_5900_plus_shape_times_225_plus_text_times_222_plus_page_times_228 as fn
    assert isinstance(fn(SAMPLES["empty"]), int)
def test_fn2_nonneg():
    from fodg import fodg_file_size_mod_937_times_5900_plus_shape_times_225_plus_text_times_222_plus_page_times_228 as fn
    for s in SAMPLES.values(): assert fn(s) >= 0
def test_fn2_path():
    from fodg import fodg_file_size_mod_937_times_5900_plus_shape_times_225_plus_text_times_222_plus_page_times_228 as fn
    assert fn(Path(SAMPLES["minimal"])) == 3163075
def test_fn2_doc():
    from fodg import fodg_file_size_mod_937_times_5900_plus_shape_times_225_plus_text_times_222_plus_page_times_228 as fn
    assert fn.__doc__ is not None and "937" in fn.__doc__
