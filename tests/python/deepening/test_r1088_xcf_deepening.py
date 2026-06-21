"""Tests for XCF analytics functions - sprint 534 (primes 929, 937)."""
from pathlib import Path
SAMPLES = {"red": "samples/by-format/xcf/valid/1x1-red-rgb.xcf", "blue": "samples/by-format/xcf/valid/1x1-rgba-blue.xcf", "gray": "samples/by-format/xcf/valid/2x2-gray.xcf"}
def test_fn1_red():
    from xcf import xcf_file_size_mod_929_times_9100_plus_image_type_times_11000_plus_width_times_1090_plus_height_times_1060 as fn
    assert fn(SAMPLES["red"]) == 1612850
def test_fn1_blue():
    from xcf import xcf_file_size_mod_929_times_9100_plus_image_type_times_11000_plus_width_times_1090_plus_height_times_1060 as fn
    assert fn(SAMPLES["blue"]) == 1621950
def test_fn1_gray():
    from xcf import xcf_file_size_mod_929_times_9100_plus_image_type_times_11000_plus_width_times_1090_plus_height_times_1060 as fn
    assert fn(SAMPLES["gray"]) == 1635100
def test_fn1_int():
    from xcf import xcf_file_size_mod_929_times_9100_plus_image_type_times_11000_plus_width_times_1090_plus_height_times_1060 as fn
    assert isinstance(fn(SAMPLES["red"]), int)
def test_fn1_nonneg():
    from xcf import xcf_file_size_mod_929_times_9100_plus_image_type_times_11000_plus_width_times_1090_plus_height_times_1060 as fn
    for s in SAMPLES.values(): assert fn(s) >= 0
def test_fn1_path():
    from xcf import xcf_file_size_mod_929_times_9100_plus_image_type_times_11000_plus_width_times_1090_plus_height_times_1060 as fn
    assert fn(Path(SAMPLES["red"])) == 1612850
def test_fn1_doc():
    from xcf import xcf_file_size_mod_929_times_9100_plus_image_type_times_11000_plus_width_times_1090_plus_height_times_1060 as fn
    assert fn.__doc__ is not None and "929" in fn.__doc__
def test_fn2_red():
    from xcf import xcf_file_size_mod_937_times_9200_plus_image_type_times_11100_plus_width_times_1100_plus_height_times_1070 as fn
    assert fn(SAMPLES["red"]) == 1630570
def test_fn2_blue():
    from xcf import xcf_file_size_mod_937_times_9200_plus_image_type_times_11100_plus_width_times_1100_plus_height_times_1070 as fn
    assert fn(SAMPLES["blue"]) == 1639770
def test_fn2_gray():
    from xcf import xcf_file_size_mod_937_times_9200_plus_image_type_times_11100_plus_width_times_1100_plus_height_times_1070 as fn
    assert fn(SAMPLES["gray"]) == 1653040
def test_fn2_int():
    from xcf import xcf_file_size_mod_937_times_9200_plus_image_type_times_11100_plus_width_times_1100_plus_height_times_1070 as fn
    assert isinstance(fn(SAMPLES["red"]), int)
def test_fn2_nonneg():
    from xcf import xcf_file_size_mod_937_times_9200_plus_image_type_times_11100_plus_width_times_1100_plus_height_times_1070 as fn
    for s in SAMPLES.values(): assert fn(s) >= 0
def test_fn2_path():
    from xcf import xcf_file_size_mod_937_times_9200_plus_image_type_times_11100_plus_width_times_1100_plus_height_times_1070 as fn
    assert fn(Path(SAMPLES["blue"])) == 1639770
def test_fn2_doc():
    from xcf import xcf_file_size_mod_937_times_9200_plus_image_type_times_11100_plus_width_times_1100_plus_height_times_1070 as fn
    assert fn.__doc__ is not None and "937" in fn.__doc__
