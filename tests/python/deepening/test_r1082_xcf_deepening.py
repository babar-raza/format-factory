"""Tests for XCF analytics functions — sprint 528 (primes 877, 881)."""
from pathlib import Path

SAMPLES = {
    "red": "samples/by-format/xcf/valid/1x1-red-rgb.xcf",
    "blue": "samples/by-format/xcf/valid/1x1-rgba-blue.xcf",
    "gray": "samples/by-format/xcf/valid/2x2-gray.xcf",
}

def test_fn1_red():
    from xcf import xcf_file_size_mod_877_times_8700_plus_image_type_times_10600_plus_width_times_1050_plus_height_times_1020 as fn
    assert fn(SAMPLES["red"]) == 1541970

def test_fn1_blue():
    from xcf import xcf_file_size_mod_877_times_8700_plus_image_type_times_10600_plus_width_times_1050_plus_height_times_1020 as fn
    assert fn(SAMPLES["blue"]) == 1550670

def test_fn1_gray():
    from xcf import xcf_file_size_mod_877_times_8700_plus_image_type_times_10600_plus_width_times_1050_plus_height_times_1020 as fn
    assert fn(SAMPLES["gray"]) == 1563340

def test_fn1_int():
    from xcf import xcf_file_size_mod_877_times_8700_plus_image_type_times_10600_plus_width_times_1050_plus_height_times_1020 as fn
    assert isinstance(fn(SAMPLES["red"]), int)

def test_fn1_nonneg():
    from xcf import xcf_file_size_mod_877_times_8700_plus_image_type_times_10600_plus_width_times_1050_plus_height_times_1020 as fn
    for s in SAMPLES.values():
        assert fn(s) >= 0

def test_fn1_path():
    from xcf import xcf_file_size_mod_877_times_8700_plus_image_type_times_10600_plus_width_times_1050_plus_height_times_1020 as fn
    assert fn(Path(SAMPLES["red"])) == 1541970

def test_fn1_doc():
    from xcf import xcf_file_size_mod_877_times_8700_plus_image_type_times_10600_plus_width_times_1050_plus_height_times_1020 as fn
    assert fn.__doc__ is not None and "877" in fn.__doc__

def test_fn2_red():
    from xcf import xcf_file_size_mod_881_times_8800_plus_image_type_times_10700_plus_width_times_1060_plus_height_times_1030 as fn
    assert fn(SAMPLES["red"]) == 1559690

def test_fn2_blue():
    from xcf import xcf_file_size_mod_881_times_8800_plus_image_type_times_10700_plus_width_times_1060_plus_height_times_1030 as fn
    assert fn(SAMPLES["blue"]) == 1568490

def test_fn2_gray():
    from xcf import xcf_file_size_mod_881_times_8800_plus_image_type_times_10700_plus_width_times_1060_plus_height_times_1030 as fn
    assert fn(SAMPLES["gray"]) == 1581280

def test_fn2_int():
    from xcf import xcf_file_size_mod_881_times_8800_plus_image_type_times_10700_plus_width_times_1060_plus_height_times_1030 as fn
    assert isinstance(fn(SAMPLES["red"]), int)

def test_fn2_nonneg():
    from xcf import xcf_file_size_mod_881_times_8800_plus_image_type_times_10700_plus_width_times_1060_plus_height_times_1030 as fn
    for s in SAMPLES.values():
        assert fn(s) >= 0

def test_fn2_path():
    from xcf import xcf_file_size_mod_881_times_8800_plus_image_type_times_10700_plus_width_times_1060_plus_height_times_1030 as fn
    assert fn(Path(SAMPLES["blue"])) == 1568490

def test_fn2_doc():
    from xcf import xcf_file_size_mod_881_times_8800_plus_image_type_times_10700_plus_width_times_1060_plus_height_times_1030 as fn
    assert fn.__doc__ is not None and "881" in fn.__doc__
