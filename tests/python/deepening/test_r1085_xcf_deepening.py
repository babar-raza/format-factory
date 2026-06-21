"""Tests for XCF analytics functions — sprint 531 (primes 911, 919)."""
from pathlib import Path
SAMPLES = {"red": "samples/by-format/xcf/valid/1x1-red-rgb.xcf", "blue": "samples/by-format/xcf/valid/1x1-rgba-blue.xcf", "gray": "samples/by-format/xcf/valid/2x2-gray.xcf"}

def test_fn1_red():
    from xcf import xcf_file_size_mod_911_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040 as fn
    assert fn(SAMPLES["red"]) == 1577410
def test_fn1_blue():
    from xcf import xcf_file_size_mod_911_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040 as fn
    assert fn(SAMPLES["blue"]) == 1586310
def test_fn1_gray():
    from xcf import xcf_file_size_mod_911_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040 as fn
    assert fn(SAMPLES["gray"]) == 1599220
def test_fn1_int():
    from xcf import xcf_file_size_mod_911_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040 as fn
    assert isinstance(fn(SAMPLES["red"]), int)
def test_fn1_nonneg():
    from xcf import xcf_file_size_mod_911_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040 as fn
    for s in SAMPLES.values(): assert fn(s) >= 0
def test_fn1_path():
    from xcf import xcf_file_size_mod_911_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040 as fn
    assert fn(Path(SAMPLES["red"])) == 1577410
def test_fn1_doc():
    from xcf import xcf_file_size_mod_911_times_8900_plus_image_type_times_10800_plus_width_times_1070_plus_height_times_1040 as fn
    assert fn.__doc__ is not None and "911" in fn.__doc__

def test_fn2_red():
    from xcf import xcf_file_size_mod_919_times_9000_plus_image_type_times_10900_plus_width_times_1080_plus_height_times_1050 as fn
    assert fn(SAMPLES["red"]) == 1595130
def test_fn2_blue():
    from xcf import xcf_file_size_mod_919_times_9000_plus_image_type_times_10900_plus_width_times_1080_plus_height_times_1050 as fn
    assert fn(SAMPLES["blue"]) == 1604130
def test_fn2_gray():
    from xcf import xcf_file_size_mod_919_times_9000_plus_image_type_times_10900_plus_width_times_1080_plus_height_times_1050 as fn
    assert fn(SAMPLES["gray"]) == 1617160
def test_fn2_int():
    from xcf import xcf_file_size_mod_919_times_9000_plus_image_type_times_10900_plus_width_times_1080_plus_height_times_1050 as fn
    assert isinstance(fn(SAMPLES["red"]), int)
def test_fn2_nonneg():
    from xcf import xcf_file_size_mod_919_times_9000_plus_image_type_times_10900_plus_width_times_1080_plus_height_times_1050 as fn
    for s in SAMPLES.values(): assert fn(s) >= 0
def test_fn2_path():
    from xcf import xcf_file_size_mod_919_times_9000_plus_image_type_times_10900_plus_width_times_1080_plus_height_times_1050 as fn
    assert fn(Path(SAMPLES["blue"])) == 1604130
def test_fn2_doc():
    from xcf import xcf_file_size_mod_919_times_9000_plus_image_type_times_10900_plus_width_times_1080_plus_height_times_1050 as fn
    assert fn.__doc__ is not None and "919" in fn.__doc__
