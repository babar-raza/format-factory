"""Sprint 609 XCF analytics deepening tests - primes 1283, 1289."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"

def test_mod1283_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1283_times_14100_plus_image_type_times_16000_plus_width_times_1590_plus_height_times_1560
    assert xcf_file_size_mod_1283_times_14100_plus_image_type_times_16000_plus_width_times_1590_plus_height_times_1560(str(RED)) == 2498850

def test_mod1283_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1283_times_14100_plus_image_type_times_16000_plus_width_times_1590_plus_height_times_1560
    assert xcf_file_size_mod_1283_times_14100_plus_image_type_times_16000_plus_width_times_1590_plus_height_times_1560(str(BLUE)) == 2512950

def test_mod1283_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1283_times_14100_plus_image_type_times_16000_plus_width_times_1590_plus_height_times_1560
    assert xcf_file_size_mod_1283_times_14100_plus_image_type_times_16000_plus_width_times_1590_plus_height_times_1560(str(GRAY)) == 2532100

def test_mod1289_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1289_times_14200_plus_image_type_times_16100_plus_width_times_1600_plus_height_times_1570
    assert xcf_file_size_mod_1289_times_14200_plus_image_type_times_16100_plus_width_times_1600_plus_height_times_1570(str(RED)) == 2516570

def test_mod1289_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1289_times_14200_plus_image_type_times_16100_plus_width_times_1600_plus_height_times_1570
    assert xcf_file_size_mod_1289_times_14200_plus_image_type_times_16100_plus_width_times_1600_plus_height_times_1570(str(BLUE)) == 2530770

def test_mod1289_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1289_times_14200_plus_image_type_times_16100_plus_width_times_1600_plus_height_times_1570
    assert xcf_file_size_mod_1289_times_14200_plus_image_type_times_16100_plus_width_times_1600_plus_height_times_1570(str(GRAY)) == 2550040

def test_mod1283_positive():
    from xcf.xcf_analytics import xcf_file_size_mod_1283_times_14100_plus_image_type_times_16000_plus_width_times_1590_plus_height_times_1560
    assert xcf_file_size_mod_1283_times_14100_plus_image_type_times_16000_plus_width_times_1590_plus_height_times_1560(str(RED)) > 0

def test_mod1289_positive():
    from xcf.xcf_analytics import xcf_file_size_mod_1289_times_14200_plus_image_type_times_16100_plus_width_times_1600_plus_height_times_1570
    assert xcf_file_size_mod_1289_times_14200_plus_image_type_times_16100_plus_width_times_1600_plus_height_times_1570(str(RED)) > 0

def test_mod1283_neq_mod1289():
    from xcf.xcf_analytics import xcf_file_size_mod_1283_times_14100_plus_image_type_times_16000_plus_width_times_1590_plus_height_times_1560, xcf_file_size_mod_1289_times_14200_plus_image_type_times_16100_plus_width_times_1600_plus_height_times_1570
    assert xcf_file_size_mod_1283_times_14100_plus_image_type_times_16000_plus_width_times_1590_plus_height_times_1560(str(GRAY)) != xcf_file_size_mod_1289_times_14200_plus_image_type_times_16100_plus_width_times_1600_plus_height_times_1570(str(GRAY))

def test_mod1283_consistent():
    from xcf.xcf_analytics import xcf_file_size_mod_1283_times_14100_plus_image_type_times_16000_plus_width_times_1590_plus_height_times_1560
    assert xcf_file_size_mod_1283_times_14100_plus_image_type_times_16000_plus_width_times_1590_plus_height_times_1560(str(BLUE)) == xcf_file_size_mod_1283_times_14100_plus_image_type_times_16000_plus_width_times_1590_plus_height_times_1560(str(BLUE))
