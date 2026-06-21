"""Sprint 579 XCF analytics deepening tests - primes 1123, 1129."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"

def test_mod1123_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1123_times_12100_plus_image_type_times_14000_plus_width_times_1390_plus_height_times_1360
    assert xcf_file_size_mod_1123_times_12100_plus_image_type_times_14000_plus_width_times_1390_plus_height_times_1360(str(RED)) == 2144450

def test_mod1123_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1123_times_12100_plus_image_type_times_14000_plus_width_times_1390_plus_height_times_1360
    assert xcf_file_size_mod_1123_times_12100_plus_image_type_times_14000_plus_width_times_1390_plus_height_times_1360(str(BLUE)) == 2156550

def test_mod1123_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1123_times_12100_plus_image_type_times_14000_plus_width_times_1390_plus_height_times_1360
    assert xcf_file_size_mod_1123_times_12100_plus_image_type_times_14000_plus_width_times_1390_plus_height_times_1360(str(GRAY)) == 2173300

def test_mod1129_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1129_times_12200_plus_image_type_times_14100_plus_width_times_1400_plus_height_times_1370
    assert xcf_file_size_mod_1129_times_12200_plus_image_type_times_14100_plus_width_times_1400_plus_height_times_1370(str(RED)) == 2162170

def test_mod1129_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1129_times_12200_plus_image_type_times_14100_plus_width_times_1400_plus_height_times_1370
    assert xcf_file_size_mod_1129_times_12200_plus_image_type_times_14100_plus_width_times_1400_plus_height_times_1370(str(BLUE)) == 2174370

def test_mod1129_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1129_times_12200_plus_image_type_times_14100_plus_width_times_1400_plus_height_times_1370
    assert xcf_file_size_mod_1129_times_12200_plus_image_type_times_14100_plus_width_times_1400_plus_height_times_1370(str(GRAY)) == 2191240

def test_mod1123_red_positive():
    from xcf.xcf_analytics import xcf_file_size_mod_1123_times_12100_plus_image_type_times_14000_plus_width_times_1390_plus_height_times_1360
    assert xcf_file_size_mod_1123_times_12100_plus_image_type_times_14000_plus_width_times_1390_plus_height_times_1360(str(RED)) > 0

def test_mod1129_red_positive():
    from xcf.xcf_analytics import xcf_file_size_mod_1129_times_12200_plus_image_type_times_14100_plus_width_times_1400_plus_height_times_1370
    assert xcf_file_size_mod_1129_times_12200_plus_image_type_times_14100_plus_width_times_1400_plus_height_times_1370(str(RED)) > 0

def test_mod1123_neq_mod1129_gray():
    from xcf.xcf_analytics import (
        xcf_file_size_mod_1123_times_12100_plus_image_type_times_14000_plus_width_times_1390_plus_height_times_1360,
        xcf_file_size_mod_1129_times_12200_plus_image_type_times_14100_plus_width_times_1400_plus_height_times_1370,
    )
    assert xcf_file_size_mod_1123_times_12100_plus_image_type_times_14000_plus_width_times_1390_plus_height_times_1360(str(GRAY)) != xcf_file_size_mod_1129_times_12200_plus_image_type_times_14100_plus_width_times_1400_plus_height_times_1370(str(GRAY))

def test_mod1123_consistent():
    from xcf.xcf_analytics import xcf_file_size_mod_1123_times_12100_plus_image_type_times_14000_plus_width_times_1390_plus_height_times_1360
    assert xcf_file_size_mod_1123_times_12100_plus_image_type_times_14000_plus_width_times_1390_plus_height_times_1360(str(BLUE)) == xcf_file_size_mod_1123_times_12100_plus_image_type_times_14000_plus_width_times_1390_plus_height_times_1360(str(BLUE))
