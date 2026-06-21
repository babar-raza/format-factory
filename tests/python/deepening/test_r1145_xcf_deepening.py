"""Sprint 591 XCF analytics deepening tests - primes 1193, 1201."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"

def test_mod1193_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1193_times_12900_plus_image_type_times_14800_plus_width_times_1470_plus_height_times_1440
    assert xcf_file_size_mod_1193_times_12900_plus_image_type_times_14800_plus_width_times_1470_plus_height_times_1440(str(RED)) == 2286210

def test_mod1193_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1193_times_12900_plus_image_type_times_14800_plus_width_times_1470_plus_height_times_1440
    assert xcf_file_size_mod_1193_times_12900_plus_image_type_times_14800_plus_width_times_1470_plus_height_times_1440(str(BLUE)) == 2299110

def test_mod1193_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1193_times_12900_plus_image_type_times_14800_plus_width_times_1470_plus_height_times_1440
    assert xcf_file_size_mod_1193_times_12900_plus_image_type_times_14800_plus_width_times_1470_plus_height_times_1440(str(GRAY)) == 2316820

def test_mod1201_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1201_times_13000_plus_image_type_times_14900_plus_width_times_1480_plus_height_times_1450
    assert xcf_file_size_mod_1201_times_13000_plus_image_type_times_14900_plus_width_times_1480_plus_height_times_1450(str(RED)) == 2303930

def test_mod1201_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1201_times_13000_plus_image_type_times_14900_plus_width_times_1480_plus_height_times_1450
    assert xcf_file_size_mod_1201_times_13000_plus_image_type_times_14900_plus_width_times_1480_plus_height_times_1450(str(BLUE)) == 2316930

def test_mod1201_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1201_times_13000_plus_image_type_times_14900_plus_width_times_1480_plus_height_times_1450
    assert xcf_file_size_mod_1201_times_13000_plus_image_type_times_14900_plus_width_times_1480_plus_height_times_1450(str(GRAY)) == 2334760

def test_mod1193_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1193_times_12900_plus_image_type_times_14800_plus_width_times_1470_plus_height_times_1440
    assert isinstance(xcf_file_size_mod_1193_times_12900_plus_image_type_times_14800_plus_width_times_1470_plus_height_times_1440(str(RED)), int)

def test_mod1193_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1193_times_12900_plus_image_type_times_14800_plus_width_times_1470_plus_height_times_1440
    assert xcf_file_size_mod_1193_times_12900_plus_image_type_times_14800_plus_width_times_1470_plus_height_times_1440(str(RED)) >= 0

def test_mod1193_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1193_times_12900_plus_image_type_times_14800_plus_width_times_1470_plus_height_times_1440
    fn2 = xcf_file_size_mod_1193_times_12900_plus_image_type_times_14800_plus_width_times_1470_plus_height_times_1440
    results = {fn2(str(RED)), fn2(str(BLUE)), fn2(str(GRAY))}
    assert len(results) == 3

def test_mod1193_importable_from_package():
    from xcf import xcf_file_size_mod_1193_times_12900_plus_image_type_times_14800_plus_width_times_1470_plus_height_times_1440
    assert callable(xcf_file_size_mod_1193_times_12900_plus_image_type_times_14800_plus_width_times_1470_plus_height_times_1440)

def test_mod1201_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1201_times_13000_plus_image_type_times_14900_plus_width_times_1480_plus_height_times_1450
    assert isinstance(xcf_file_size_mod_1201_times_13000_plus_image_type_times_14900_plus_width_times_1480_plus_height_times_1450(str(RED)), int)

def test_mod1201_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1201_times_13000_plus_image_type_times_14900_plus_width_times_1480_plus_height_times_1450
    assert xcf_file_size_mod_1201_times_13000_plus_image_type_times_14900_plus_width_times_1480_plus_height_times_1450(str(RED)) >= 0

def test_mod1201_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1201_times_13000_plus_image_type_times_14900_plus_width_times_1480_plus_height_times_1450
    fn2 = xcf_file_size_mod_1201_times_13000_plus_image_type_times_14900_plus_width_times_1480_plus_height_times_1450
    results = {fn2(str(RED)), fn2(str(BLUE)), fn2(str(GRAY))}
    assert len(results) == 3

def test_mod1201_importable_from_package():
    from xcf import xcf_file_size_mod_1201_times_13000_plus_image_type_times_14900_plus_width_times_1480_plus_height_times_1450
    assert callable(xcf_file_size_mod_1201_times_13000_plus_image_type_times_14900_plus_width_times_1480_plus_height_times_1450)
