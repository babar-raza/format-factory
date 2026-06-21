"""Tests for FODG analytics functions — sprint 524 (primes 859, 863)."""
import pytest
from pathlib import Path

SAMPLES = {
    "empty": "samples/by-format/fodg/empty-page.fodg",
    "minimal": "samples/by-format/fodg/minimal-drawing.fodg",
    "shapes": "samples/by-format/fodg/shapes-basic.fodg",
}

# ---------------------------------------------------------------------------
# FN1: fodg_file_size_mod_859_times_5200_plus_shape_times_211_plus_text_times_208_plus_page_times_214
# ---------------------------------------------------------------------------

def test_fn1_empty():
    from fodg import fodg_file_size_mod_859_times_5200_plus_shape_times_211_plus_text_times_208_plus_page_times_214 as fn
    assert fn(SAMPLES["empty"]) == 1009014

def test_fn1_minimal():
    from fodg import fodg_file_size_mod_859_times_5200_plus_shape_times_211_plus_text_times_208_plus_page_times_214 as fn
    assert fn(SAMPLES["minimal"]) == 3193433

def test_fn1_shapes():
    from fodg import fodg_file_size_mod_859_times_5200_plus_shape_times_211_plus_text_times_208_plus_page_times_214 as fn
    assert fn(SAMPLES["shapes"]) == 4000063

def test_fn1_returns_int():
    from fodg import fodg_file_size_mod_859_times_5200_plus_shape_times_211_plus_text_times_208_plus_page_times_214 as fn
    assert isinstance(fn(SAMPLES["empty"]), int)

def test_fn1_nonnegative():
    from fodg import fodg_file_size_mod_859_times_5200_plus_shape_times_211_plus_text_times_208_plus_page_times_214 as fn
    for s in SAMPLES.values():
        assert fn(s) >= 0

def test_fn1_pathlib():
    from fodg import fodg_file_size_mod_859_times_5200_plus_shape_times_211_plus_text_times_208_plus_page_times_214 as fn
    assert fn(Path(SAMPLES["empty"])) == 1009014

def test_fn1_docstring():
    from fodg import fodg_file_size_mod_859_times_5200_plus_shape_times_211_plus_text_times_208_plus_page_times_214 as fn
    assert fn.__doc__ is not None and "859" in fn.__doc__

# ---------------------------------------------------------------------------
# FN2: fodg_file_size_mod_863_times_5300_plus_shape_times_213_plus_text_times_210_plus_page_times_216
# ---------------------------------------------------------------------------

def test_fn2_empty():
    from fodg import fodg_file_size_mod_863_times_5300_plus_shape_times_213_plus_text_times_210_plus_page_times_216 as fn
    assert fn(SAMPLES["empty"]) == 1007216

def test_fn2_minimal():
    from fodg import fodg_file_size_mod_863_times_5300_plus_shape_times_213_plus_text_times_210_plus_page_times_216 as fn
    assert fn(SAMPLES["minimal"]) == 3233639

def test_fn2_shapes():
    from fodg import fodg_file_size_mod_863_times_5300_plus_shape_times_213_plus_text_times_210_plus_page_times_216 as fn
    assert fn(SAMPLES["shapes"]) == 4055775

def test_fn2_returns_int():
    from fodg import fodg_file_size_mod_863_times_5300_plus_shape_times_213_plus_text_times_210_plus_page_times_216 as fn
    assert isinstance(fn(SAMPLES["empty"]), int)

def test_fn2_nonnegative():
    from fodg import fodg_file_size_mod_863_times_5300_plus_shape_times_213_plus_text_times_210_plus_page_times_216 as fn
    for s in SAMPLES.values():
        assert fn(s) >= 0

def test_fn2_pathlib():
    from fodg import fodg_file_size_mod_863_times_5300_plus_shape_times_213_plus_text_times_210_plus_page_times_216 as fn
    assert fn(Path(SAMPLES["minimal"])) == 3233639

def test_fn2_docstring():
    from fodg import fodg_file_size_mod_863_times_5300_plus_shape_times_213_plus_text_times_210_plus_page_times_216 as fn
    assert fn.__doc__ is not None and "863" in fn.__doc__
