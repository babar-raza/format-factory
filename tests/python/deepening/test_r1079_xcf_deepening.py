"""Tests for XCF analytics functions — sprint 525 (primes 859, 863)."""
from pathlib import Path

SAMPLES = {
    "red": "samples/by-format/xcf/valid/1x1-red-rgb.xcf",
    "blue": "samples/by-format/xcf/valid/1x1-rgba-blue.xcf",
    "gray": "samples/by-format/xcf/valid/2x2-gray.xcf",
}

# FN1: xcf_file_size_mod_859_times_8500_plus_image_type_times_10400_plus_width_times_1030_plus_height_times_1000

def test_fn1_red():
    from xcf import xcf_file_size_mod_859_times_8500_plus_image_type_times_10400_plus_width_times_1030_plus_height_times_1000 as fn
    assert fn(SAMPLES["red"]) == 1506530

def test_fn1_blue():
    from xcf import xcf_file_size_mod_859_times_8500_plus_image_type_times_10400_plus_width_times_1030_plus_height_times_1000 as fn
    assert fn(SAMPLES["blue"]) == 1515030

def test_fn1_gray():
    from xcf import xcf_file_size_mod_859_times_8500_plus_image_type_times_10400_plus_width_times_1030_plus_height_times_1000 as fn
    assert fn(SAMPLES["gray"]) == 1527460

def test_fn1_int():
    from xcf import xcf_file_size_mod_859_times_8500_plus_image_type_times_10400_plus_width_times_1030_plus_height_times_1000 as fn
    assert isinstance(fn(SAMPLES["red"]), int)

def test_fn1_nonneg():
    from xcf import xcf_file_size_mod_859_times_8500_plus_image_type_times_10400_plus_width_times_1030_plus_height_times_1000 as fn
    for s in SAMPLES.values():
        assert fn(s) >= 0

def test_fn1_path():
    from xcf import xcf_file_size_mod_859_times_8500_plus_image_type_times_10400_plus_width_times_1030_plus_height_times_1000 as fn
    assert fn(Path(SAMPLES["red"])) == 1506530

def test_fn1_doc():
    from xcf import xcf_file_size_mod_859_times_8500_plus_image_type_times_10400_plus_width_times_1030_plus_height_times_1000 as fn
    assert fn.__doc__ is not None and "859" in fn.__doc__

# FN2: xcf_file_size_mod_863_times_8600_plus_image_type_times_10500_plus_width_times_1040_plus_height_times_1010

def test_fn2_red():
    from xcf import xcf_file_size_mod_863_times_8600_plus_image_type_times_10500_plus_width_times_1040_plus_height_times_1010 as fn
    assert fn(SAMPLES["red"]) == 1524250

def test_fn2_blue():
    from xcf import xcf_file_size_mod_863_times_8600_plus_image_type_times_10500_plus_width_times_1040_plus_height_times_1010 as fn
    assert fn(SAMPLES["blue"]) == 1532850

def test_fn2_gray():
    from xcf import xcf_file_size_mod_863_times_8600_plus_image_type_times_10500_plus_width_times_1040_plus_height_times_1010 as fn
    assert fn(SAMPLES["gray"]) == 1545400

def test_fn2_int():
    from xcf import xcf_file_size_mod_863_times_8600_plus_image_type_times_10500_plus_width_times_1040_plus_height_times_1010 as fn
    assert isinstance(fn(SAMPLES["red"]), int)

def test_fn2_nonneg():
    from xcf import xcf_file_size_mod_863_times_8600_plus_image_type_times_10500_plus_width_times_1040_plus_height_times_1010 as fn
    for s in SAMPLES.values():
        assert fn(s) >= 0

def test_fn2_path():
    from xcf import xcf_file_size_mod_863_times_8600_plus_image_type_times_10500_plus_width_times_1040_plus_height_times_1010 as fn
    assert fn(Path(SAMPLES["blue"])) == 1532850

def test_fn2_doc():
    from xcf import xcf_file_size_mod_863_times_8600_plus_image_type_times_10500_plus_width_times_1040_plus_height_times_1010 as fn
    assert fn.__doc__ is not None and "863" in fn.__doc__
