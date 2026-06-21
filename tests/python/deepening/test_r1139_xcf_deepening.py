"""Sprint 585 XCF analytics deepening tests - primes 1163, 1171."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"

def test_mod1163_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1163_times_12500_plus_image_type_times_14400_plus_width_times_1430_plus_height_times_1400
    assert xcf_file_size_mod_1163_times_12500_plus_image_type_times_14400_plus_width_times_1430_plus_height_times_1400(str(RED)) == 2215330

def test_mod1163_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1163_times_12500_plus_image_type_times_14400_plus_width_times_1430_plus_height_times_1400
    assert xcf_file_size_mod_1163_times_12500_plus_image_type_times_14400_plus_width_times_1430_plus_height_times_1400(str(BLUE)) == 2227830

def test_mod1163_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1163_times_12500_plus_image_type_times_14400_plus_width_times_1430_plus_height_times_1400
    assert xcf_file_size_mod_1163_times_12500_plus_image_type_times_14400_plus_width_times_1430_plus_height_times_1400(str(GRAY)) == 2245060

def test_mod1171_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1171_times_12600_plus_image_type_times_14500_plus_width_times_1440_plus_height_times_1410
    assert xcf_file_size_mod_1171_times_12600_plus_image_type_times_14500_plus_width_times_1440_plus_height_times_1410(str(RED)) == 2233050

def test_mod1171_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1171_times_12600_plus_image_type_times_14500_plus_width_times_1440_plus_height_times_1410
    assert xcf_file_size_mod_1171_times_12600_plus_image_type_times_14500_plus_width_times_1440_plus_height_times_1410(str(BLUE)) == 2245650

def test_mod1171_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1171_times_12600_plus_image_type_times_14500_plus_width_times_1440_plus_height_times_1410
    assert xcf_file_size_mod_1171_times_12600_plus_image_type_times_14500_plus_width_times_1440_plus_height_times_1410(str(GRAY)) == 2263000

def test_mod1163_positive():
    from xcf.xcf_analytics import xcf_file_size_mod_1163_times_12500_plus_image_type_times_14400_plus_width_times_1430_plus_height_times_1400
    assert xcf_file_size_mod_1163_times_12500_plus_image_type_times_14400_plus_width_times_1430_plus_height_times_1400(str(RED)) > 0

def test_mod1171_positive():
    from xcf.xcf_analytics import xcf_file_size_mod_1171_times_12600_plus_image_type_times_14500_plus_width_times_1440_plus_height_times_1410
    assert xcf_file_size_mod_1171_times_12600_plus_image_type_times_14500_plus_width_times_1440_plus_height_times_1410(str(RED)) > 0

def test_mod1163_neq_mod1171():
    from xcf.xcf_analytics import xcf_file_size_mod_1163_times_12500_plus_image_type_times_14400_plus_width_times_1430_plus_height_times_1400, xcf_file_size_mod_1171_times_12600_plus_image_type_times_14500_plus_width_times_1440_plus_height_times_1410
    assert xcf_file_size_mod_1163_times_12500_plus_image_type_times_14400_plus_width_times_1430_plus_height_times_1400(str(GRAY)) != xcf_file_size_mod_1171_times_12600_plus_image_type_times_14500_plus_width_times_1440_plus_height_times_1410(str(GRAY))

def test_mod1163_consistent():
    from xcf.xcf_analytics import xcf_file_size_mod_1163_times_12500_plus_image_type_times_14400_plus_width_times_1430_plus_height_times_1400
    assert xcf_file_size_mod_1163_times_12500_plus_image_type_times_14400_plus_width_times_1430_plus_height_times_1400(str(BLUE)) == xcf_file_size_mod_1163_times_12500_plus_image_type_times_14400_plus_width_times_1430_plus_height_times_1400(str(BLUE))
