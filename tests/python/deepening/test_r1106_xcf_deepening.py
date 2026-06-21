"""Sprint 552 XCF analytics deepening tests - primes 1013, 1019."""
import pytest
from pathlib import Path

RED = Path("samples/by-format/xcf/valid/1x1-red-rgb.xcf")
BLUE = Path("samples/by-format/xcf/valid/1x1-rgba-blue.xcf")
GRAY = Path("samples/by-format/xcf/valid/2x2-gray.xcf")

def test_fn1_red():
    from xcf import xcf_file_size_mod_1013_times_10300_plus_image_type_times_12200_plus_width_times_1210_plus_height_times_1180 as fn
    assert fn(str(RED)) == 1825490
def test_fn1_blue():
    from xcf import xcf_file_size_mod_1013_times_10300_plus_image_type_times_12200_plus_width_times_1210_plus_height_times_1180 as fn
    assert fn(str(BLUE)) == 1835790
def test_fn1_gray():
    from xcf import xcf_file_size_mod_1013_times_10300_plus_image_type_times_12200_plus_width_times_1210_plus_height_times_1180 as fn
    assert fn(str(GRAY)) == 1850380
def test_fn1_int():
    from xcf import xcf_file_size_mod_1013_times_10300_plus_image_type_times_12200_plus_width_times_1210_plus_height_times_1180 as fn
    assert isinstance(fn(str(RED)), int)
def test_fn1_nonneg():
    from xcf import xcf_file_size_mod_1013_times_10300_plus_image_type_times_12200_plus_width_times_1210_plus_height_times_1180 as fn
    for s in [RED, BLUE, GRAY]: assert fn(str(s)) >= 0
def test_fn1_path():
    from xcf import xcf_file_size_mod_1013_times_10300_plus_image_type_times_12200_plus_width_times_1210_plus_height_times_1180 as fn
    assert fn(RED) == 1825490
def test_fn1_doc():
    from xcf import xcf_file_size_mod_1013_times_10300_plus_image_type_times_12200_plus_width_times_1210_plus_height_times_1180 as fn
    assert fn.__doc__ is not None and "1013" in fn.__doc__
def test_fn2_red():
    from xcf import xcf_file_size_mod_1019_times_10400_plus_image_type_times_12300_plus_width_times_1220_plus_height_times_1190 as fn
    assert fn(str(RED)) == 1843210
def test_fn2_blue():
    from xcf import xcf_file_size_mod_1019_times_10400_plus_image_type_times_12300_plus_width_times_1220_plus_height_times_1190 as fn
    assert fn(str(BLUE)) == 1853610
def test_fn2_gray():
    from xcf import xcf_file_size_mod_1019_times_10400_plus_image_type_times_12300_plus_width_times_1220_plus_height_times_1190 as fn
    assert fn(str(GRAY)) == 1868320
def test_fn2_int():
    from xcf import xcf_file_size_mod_1019_times_10400_plus_image_type_times_12300_plus_width_times_1220_plus_height_times_1190 as fn
    assert isinstance(fn(str(RED)), int)
def test_fn2_nonneg():
    from xcf import xcf_file_size_mod_1019_times_10400_plus_image_type_times_12300_plus_width_times_1220_plus_height_times_1190 as fn
    for s in [RED, BLUE, GRAY]: assert fn(str(s)) >= 0
def test_fn2_path():
    from xcf import xcf_file_size_mod_1019_times_10400_plus_image_type_times_12300_plus_width_times_1220_plus_height_times_1190 as fn
    assert fn(BLUE) == 1853610
def test_fn2_doc():
    from xcf import xcf_file_size_mod_1019_times_10400_plus_image_type_times_12300_plus_width_times_1220_plus_height_times_1190 as fn
    assert fn.__doc__ is not None and "1019" in fn.__doc__
