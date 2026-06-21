"""Sprint 582 XCF analytics deepening tests - primes 1151, 1153."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"

def test_mod1151_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1151_times_12300_plus_image_type_times_14200_plus_width_times_1410_plus_height_times_1380
    assert xcf_file_size_mod_1151_times_12300_plus_image_type_times_14200_plus_width_times_1410_plus_height_times_1380(str(RED)) == 2179890

def test_mod1151_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1151_times_12300_plus_image_type_times_14200_plus_width_times_1410_plus_height_times_1380
    assert xcf_file_size_mod_1151_times_12300_plus_image_type_times_14200_plus_width_times_1410_plus_height_times_1380(str(BLUE)) == 2192190

def test_mod1151_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1151_times_12300_plus_image_type_times_14200_plus_width_times_1410_plus_height_times_1380
    assert xcf_file_size_mod_1151_times_12300_plus_image_type_times_14200_plus_width_times_1410_plus_height_times_1380(str(GRAY)) == 2209180

def test_mod1153_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1153_times_12400_plus_image_type_times_14300_plus_width_times_1420_plus_height_times_1390
    assert xcf_file_size_mod_1153_times_12400_plus_image_type_times_14300_plus_width_times_1420_plus_height_times_1390(str(RED)) == 2197610

def test_mod1153_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1153_times_12400_plus_image_type_times_14300_plus_width_times_1420_plus_height_times_1390
    assert xcf_file_size_mod_1153_times_12400_plus_image_type_times_14300_plus_width_times_1420_plus_height_times_1390(str(BLUE)) == 2210010

def test_mod1153_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1153_times_12400_plus_image_type_times_14300_plus_width_times_1420_plus_height_times_1390
    assert xcf_file_size_mod_1153_times_12400_plus_image_type_times_14300_plus_width_times_1420_plus_height_times_1390(str(GRAY)) == 2227120

def test_mod1151_positive():
    from xcf.xcf_analytics import xcf_file_size_mod_1151_times_12300_plus_image_type_times_14200_plus_width_times_1410_plus_height_times_1380
    assert xcf_file_size_mod_1151_times_12300_plus_image_type_times_14200_plus_width_times_1410_plus_height_times_1380(str(RED)) > 0

def test_mod1153_positive():
    from xcf.xcf_analytics import xcf_file_size_mod_1153_times_12400_plus_image_type_times_14300_plus_width_times_1420_plus_height_times_1390
    assert xcf_file_size_mod_1153_times_12400_plus_image_type_times_14300_plus_width_times_1420_plus_height_times_1390(str(RED)) > 0

def test_mod1151_neq_mod1153():
    from xcf.xcf_analytics import xcf_file_size_mod_1151_times_12300_plus_image_type_times_14200_plus_width_times_1410_plus_height_times_1380, xcf_file_size_mod_1153_times_12400_plus_image_type_times_14300_plus_width_times_1420_plus_height_times_1390
    assert xcf_file_size_mod_1151_times_12300_plus_image_type_times_14200_plus_width_times_1410_plus_height_times_1380(str(GRAY)) != xcf_file_size_mod_1153_times_12400_plus_image_type_times_14300_plus_width_times_1420_plus_height_times_1390(str(GRAY))

def test_mod1151_consistent():
    from xcf.xcf_analytics import xcf_file_size_mod_1151_times_12300_plus_image_type_times_14200_plus_width_times_1410_plus_height_times_1380
    assert xcf_file_size_mod_1151_times_12300_plus_image_type_times_14200_plus_width_times_1410_plus_height_times_1380(str(BLUE)) == xcf_file_size_mod_1151_times_12300_plus_image_type_times_14200_plus_width_times_1410_plus_height_times_1380(str(BLUE))
