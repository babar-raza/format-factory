"""Tests for FODG analytics functions — sprint 527 (primes 877, 881)."""
from pathlib import Path

SAMPLES = {
    "empty": "samples/by-format/fodg/empty-page.fodg",
    "minimal": "samples/by-format/fodg/minimal-drawing.fodg",
    "shapes": "samples/by-format/fodg/shapes-basic.fodg",
}

def test_fn1_empty():
    from fodg import fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218 as fn
    assert fn(SAMPLES["empty"]) == 950618

def test_fn1_minimal():
    from fodg import fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218 as fn
    assert fn(SAMPLES["minimal"]) == 3219045

def test_fn1_shapes():
    from fodg import fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218 as fn
    assert fn(SAMPLES["shapes"]) == 4056687

def test_fn1_int():
    from fodg import fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218 as fn
    assert isinstance(fn(SAMPLES["empty"]), int)

def test_fn1_nonneg():
    from fodg import fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218 as fn
    for s in SAMPLES.values():
        assert fn(s) >= 0

def test_fn1_path():
    from fodg import fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218 as fn
    assert fn(Path(SAMPLES["empty"])) == 950618

def test_fn1_doc():
    from fodg import fodg_file_size_mod_877_times_5400_plus_shape_times_215_plus_text_times_212_plus_page_times_218 as fn
    assert fn.__doc__ is not None and "877" in fn.__doc__

def test_fn2_empty():
    from fodg import fodg_file_size_mod_881_times_5500_plus_shape_times_217_plus_text_times_214_plus_page_times_220 as fn
    assert fn(SAMPLES["empty"]) == 946220

def test_fn2_minimal():
    from fodg import fodg_file_size_mod_881_times_5500_plus_shape_times_217_plus_text_times_214_plus_page_times_220 as fn
    assert fn(SAMPLES["minimal"]) == 3256651

def test_fn2_shapes():
    from fodg import fodg_file_size_mod_881_times_5500_plus_shape_times_217_plus_text_times_214_plus_page_times_220 as fn
    assert fn(SAMPLES["shapes"]) == 4109799

def test_fn2_int():
    from fodg import fodg_file_size_mod_881_times_5500_plus_shape_times_217_plus_text_times_214_plus_page_times_220 as fn
    assert isinstance(fn(SAMPLES["empty"]), int)

def test_fn2_nonneg():
    from fodg import fodg_file_size_mod_881_times_5500_plus_shape_times_217_plus_text_times_214_plus_page_times_220 as fn
    for s in SAMPLES.values():
        assert fn(s) >= 0

def test_fn2_path():
    from fodg import fodg_file_size_mod_881_times_5500_plus_shape_times_217_plus_text_times_214_plus_page_times_220 as fn
    assert fn(Path(SAMPLES["minimal"])) == 3256651

def test_fn2_doc():
    from fodg import fodg_file_size_mod_881_times_5500_plus_shape_times_217_plus_text_times_214_plus_page_times_220 as fn
    assert fn.__doc__ is not None and "881" in fn.__doc__
