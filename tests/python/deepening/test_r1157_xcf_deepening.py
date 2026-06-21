"""Sprint 603 XCF analytics deepening tests - primes 1249, 1259."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"

def test_mod1249_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1249_times_13700_plus_image_type_times_15600_plus_width_times_1550_plus_height_times_1520
    assert xcf_file_size_mod_1249_times_13700_plus_image_type_times_15600_plus_width_times_1550_plus_height_times_1520(str(RED)) == 2427970

def test_mod1249_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1249_times_13700_plus_image_type_times_15600_plus_width_times_1550_plus_height_times_1520
    assert xcf_file_size_mod_1249_times_13700_plus_image_type_times_15600_plus_width_times_1550_plus_height_times_1520(str(BLUE)) == 2441670

def test_mod1249_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1249_times_13700_plus_image_type_times_15600_plus_width_times_1550_plus_height_times_1520
    assert xcf_file_size_mod_1249_times_13700_plus_image_type_times_15600_plus_width_times_1550_plus_height_times_1520(str(GRAY)) == 2460340

def test_mod1259_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1259_times_13800_plus_image_type_times_15700_plus_width_times_1560_plus_height_times_1530
    assert xcf_file_size_mod_1259_times_13800_plus_image_type_times_15700_plus_width_times_1560_plus_height_times_1530(str(RED)) == 2445690

def test_mod1259_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1259_times_13800_plus_image_type_times_15700_plus_width_times_1560_plus_height_times_1530
    assert xcf_file_size_mod_1259_times_13800_plus_image_type_times_15700_plus_width_times_1560_plus_height_times_1530(str(BLUE)) == 2459490

def test_mod1259_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1259_times_13800_plus_image_type_times_15700_plus_width_times_1560_plus_height_times_1530
    assert xcf_file_size_mod_1259_times_13800_plus_image_type_times_15700_plus_width_times_1560_plus_height_times_1530(str(GRAY)) == 2478280

def test_mod1249_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1249_times_13700_plus_image_type_times_15600_plus_width_times_1550_plus_height_times_1520
    assert isinstance(xcf_file_size_mod_1249_times_13700_plus_image_type_times_15600_plus_width_times_1550_plus_height_times_1520(str(RED)), int)

def test_mod1249_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1249_times_13700_plus_image_type_times_15600_plus_width_times_1550_plus_height_times_1520
    assert xcf_file_size_mod_1249_times_13700_plus_image_type_times_15600_plus_width_times_1550_plus_height_times_1520(str(RED)) >= 0

def test_mod1249_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1249_times_13700_plus_image_type_times_15600_plus_width_times_1550_plus_height_times_1520
    fn2 = xcf_file_size_mod_1249_times_13700_plus_image_type_times_15600_plus_width_times_1550_plus_height_times_1520
    results = {fn2(str(RED)), fn2(str(BLUE)), fn2(str(GRAY))}
    assert len(results) == 3

def test_mod1249_importable_from_package():
    from xcf import xcf_file_size_mod_1249_times_13700_plus_image_type_times_15600_plus_width_times_1550_plus_height_times_1520
    assert callable(xcf_file_size_mod_1249_times_13700_plus_image_type_times_15600_plus_width_times_1550_plus_height_times_1520)

def test_mod1259_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1259_times_13800_plus_image_type_times_15700_plus_width_times_1560_plus_height_times_1530
    assert isinstance(xcf_file_size_mod_1259_times_13800_plus_image_type_times_15700_plus_width_times_1560_plus_height_times_1530(str(RED)), int)

def test_mod1259_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1259_times_13800_plus_image_type_times_15700_plus_width_times_1560_plus_height_times_1530
    assert xcf_file_size_mod_1259_times_13800_plus_image_type_times_15700_plus_width_times_1560_plus_height_times_1530(str(RED)) >= 0

def test_mod1259_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1259_times_13800_plus_image_type_times_15700_plus_width_times_1560_plus_height_times_1530
    fn2 = xcf_file_size_mod_1259_times_13800_plus_image_type_times_15700_plus_width_times_1560_plus_height_times_1530
    results = {fn2(str(RED)), fn2(str(BLUE)), fn2(str(GRAY))}
    assert len(results) == 3

def test_mod1259_importable_from_package():
    from xcf import xcf_file_size_mod_1259_times_13800_plus_image_type_times_15700_plus_width_times_1560_plus_height_times_1530
    assert callable(xcf_file_size_mod_1259_times_13800_plus_image_type_times_15700_plus_width_times_1560_plus_height_times_1530)
