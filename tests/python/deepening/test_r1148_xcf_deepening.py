"""Sprint 594 XCF analytics deepening tests - primes 1213, 1217."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"

def test_mod1213_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1213_times_13100_plus_image_type_times_15000_plus_width_times_1490_plus_height_times_1460
    assert xcf_file_size_mod_1213_times_13100_plus_image_type_times_15000_plus_width_times_1490_plus_height_times_1460(str(RED)) == 2321650

def test_mod1213_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1213_times_13100_plus_image_type_times_15000_plus_width_times_1490_plus_height_times_1460
    assert xcf_file_size_mod_1213_times_13100_plus_image_type_times_15000_plus_width_times_1490_plus_height_times_1460(str(BLUE)) == 2334750

def test_mod1213_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1213_times_13100_plus_image_type_times_15000_plus_width_times_1490_plus_height_times_1460
    assert xcf_file_size_mod_1213_times_13100_plus_image_type_times_15000_plus_width_times_1490_plus_height_times_1460(str(GRAY)) == 2352700

def test_mod1217_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1217_times_13200_plus_image_type_times_15100_plus_width_times_1500_plus_height_times_1470
    assert xcf_file_size_mod_1217_times_13200_plus_image_type_times_15100_plus_width_times_1500_plus_height_times_1470(str(RED)) == 2339370

def test_mod1217_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1217_times_13200_plus_image_type_times_15100_plus_width_times_1500_plus_height_times_1470
    assert xcf_file_size_mod_1217_times_13200_plus_image_type_times_15100_plus_width_times_1500_plus_height_times_1470(str(BLUE)) == 2352570

def test_mod1217_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1217_times_13200_plus_image_type_times_15100_plus_width_times_1500_plus_height_times_1470
    assert xcf_file_size_mod_1217_times_13200_plus_image_type_times_15100_plus_width_times_1500_plus_height_times_1470(str(GRAY)) == 2370640

def test_mod1213_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1213_times_13100_plus_image_type_times_15000_plus_width_times_1490_plus_height_times_1460
    assert isinstance(xcf_file_size_mod_1213_times_13100_plus_image_type_times_15000_plus_width_times_1490_plus_height_times_1460(str(RED)), int)

def test_mod1213_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1213_times_13100_plus_image_type_times_15000_plus_width_times_1490_plus_height_times_1460
    assert xcf_file_size_mod_1213_times_13100_plus_image_type_times_15000_plus_width_times_1490_plus_height_times_1460(str(RED)) >= 0

def test_mod1213_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1213_times_13100_plus_image_type_times_15000_plus_width_times_1490_plus_height_times_1460
    fn2 = xcf_file_size_mod_1213_times_13100_plus_image_type_times_15000_plus_width_times_1490_plus_height_times_1460
    results = {fn2(str(RED)), fn2(str(BLUE)), fn2(str(GRAY))}
    assert len(results) == 3

def test_mod1213_importable_from_package():
    from xcf import xcf_file_size_mod_1213_times_13100_plus_image_type_times_15000_plus_width_times_1490_plus_height_times_1460
    assert callable(xcf_file_size_mod_1213_times_13100_plus_image_type_times_15000_plus_width_times_1490_plus_height_times_1460)

def test_mod1217_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1217_times_13200_plus_image_type_times_15100_plus_width_times_1500_plus_height_times_1470
    assert isinstance(xcf_file_size_mod_1217_times_13200_plus_image_type_times_15100_plus_width_times_1500_plus_height_times_1470(str(RED)), int)

def test_mod1217_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1217_times_13200_plus_image_type_times_15100_plus_width_times_1500_plus_height_times_1470
    assert xcf_file_size_mod_1217_times_13200_plus_image_type_times_15100_plus_width_times_1500_plus_height_times_1470(str(RED)) >= 0

def test_mod1217_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1217_times_13200_plus_image_type_times_15100_plus_width_times_1500_plus_height_times_1470
    fn2 = xcf_file_size_mod_1217_times_13200_plus_image_type_times_15100_plus_width_times_1500_plus_height_times_1470
    results = {fn2(str(RED)), fn2(str(BLUE)), fn2(str(GRAY))}
    assert len(results) == 3

def test_mod1217_importable_from_package():
    from xcf import xcf_file_size_mod_1217_times_13200_plus_image_type_times_15100_plus_width_times_1500_plus_height_times_1470
    assert callable(xcf_file_size_mod_1217_times_13200_plus_image_type_times_15100_plus_width_times_1500_plus_height_times_1470)
