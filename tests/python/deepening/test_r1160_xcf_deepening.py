"""Sprint 606 XCF analytics deepening tests - primes 1277, 1279."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"

def test_mod1277_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1277_times_13900_plus_image_type_times_15800_plus_width_times_1570_plus_height_times_1540
    assert xcf_file_size_mod_1277_times_13900_plus_image_type_times_15800_plus_width_times_1570_plus_height_times_1540(str(RED)) == 2463410

def test_mod1277_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1277_times_13900_plus_image_type_times_15800_plus_width_times_1570_plus_height_times_1540
    assert xcf_file_size_mod_1277_times_13900_plus_image_type_times_15800_plus_width_times_1570_plus_height_times_1540(str(BLUE)) == 2477310

def test_mod1277_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1277_times_13900_plus_image_type_times_15800_plus_width_times_1570_plus_height_times_1540
    assert xcf_file_size_mod_1277_times_13900_plus_image_type_times_15800_plus_width_times_1570_plus_height_times_1540(str(GRAY)) == 2496220

def test_mod1279_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1279_times_14000_plus_image_type_times_15900_plus_width_times_1580_plus_height_times_1550
    assert xcf_file_size_mod_1279_times_14000_plus_image_type_times_15900_plus_width_times_1580_plus_height_times_1550(str(RED)) == 2481130

def test_mod1279_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1279_times_14000_plus_image_type_times_15900_plus_width_times_1580_plus_height_times_1550
    assert xcf_file_size_mod_1279_times_14000_plus_image_type_times_15900_plus_width_times_1580_plus_height_times_1550(str(BLUE)) == 2495130

def test_mod1279_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1279_times_14000_plus_image_type_times_15900_plus_width_times_1580_plus_height_times_1550
    assert xcf_file_size_mod_1279_times_14000_plus_image_type_times_15900_plus_width_times_1580_plus_height_times_1550(str(GRAY)) == 2514160

def test_mod1277_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1277_times_13900_plus_image_type_times_15800_plus_width_times_1570_plus_height_times_1540
    assert isinstance(xcf_file_size_mod_1277_times_13900_plus_image_type_times_15800_plus_width_times_1570_plus_height_times_1540(str(RED)), int)

def test_mod1277_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1277_times_13900_plus_image_type_times_15800_plus_width_times_1570_plus_height_times_1540
    assert xcf_file_size_mod_1277_times_13900_plus_image_type_times_15800_plus_width_times_1570_plus_height_times_1540(str(RED)) >= 0

def test_mod1277_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1277_times_13900_plus_image_type_times_15800_plus_width_times_1570_plus_height_times_1540
    fn2 = xcf_file_size_mod_1277_times_13900_plus_image_type_times_15800_plus_width_times_1570_plus_height_times_1540
    results = {fn2(str(RED)), fn2(str(BLUE)), fn2(str(GRAY))}
    assert len(results) == 3

def test_mod1277_importable_from_package():
    from xcf import xcf_file_size_mod_1277_times_13900_plus_image_type_times_15800_plus_width_times_1570_plus_height_times_1540
    assert callable(xcf_file_size_mod_1277_times_13900_plus_image_type_times_15800_plus_width_times_1570_plus_height_times_1540)

def test_mod1279_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1279_times_14000_plus_image_type_times_15900_plus_width_times_1580_plus_height_times_1550
    assert isinstance(xcf_file_size_mod_1279_times_14000_plus_image_type_times_15900_plus_width_times_1580_plus_height_times_1550(str(RED)), int)

def test_mod1279_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1279_times_14000_plus_image_type_times_15900_plus_width_times_1580_plus_height_times_1550
    assert xcf_file_size_mod_1279_times_14000_plus_image_type_times_15900_plus_width_times_1580_plus_height_times_1550(str(RED)) >= 0

def test_mod1279_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1279_times_14000_plus_image_type_times_15900_plus_width_times_1580_plus_height_times_1550
    fn2 = xcf_file_size_mod_1279_times_14000_plus_image_type_times_15900_plus_width_times_1580_plus_height_times_1550
    results = {fn2(str(RED)), fn2(str(BLUE)), fn2(str(GRAY))}
    assert len(results) == 3

def test_mod1279_importable_from_package():
    from xcf import xcf_file_size_mod_1279_times_14000_plus_image_type_times_15900_plus_width_times_1580_plus_height_times_1550
    assert callable(xcf_file_size_mod_1279_times_14000_plus_image_type_times_15900_plus_width_times_1580_plus_height_times_1550)
