"""Sprint 588 XCF analytics deepening tests - primes 1181, 1187."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"

def test_mod1181_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1181_times_12700_plus_image_type_times_14600_plus_width_times_1450_plus_height_times_1420
    assert xcf_file_size_mod_1181_times_12700_plus_image_type_times_14600_plus_width_times_1450_plus_height_times_1420(str(RED)) == 2250770

def test_mod1181_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1181_times_12700_plus_image_type_times_14600_plus_width_times_1450_plus_height_times_1420
    assert xcf_file_size_mod_1181_times_12700_plus_image_type_times_14600_plus_width_times_1450_plus_height_times_1420(str(BLUE)) == 2263470

def test_mod1181_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1181_times_12700_plus_image_type_times_14600_plus_width_times_1450_plus_height_times_1420
    assert xcf_file_size_mod_1181_times_12700_plus_image_type_times_14600_plus_width_times_1450_plus_height_times_1420(str(GRAY)) == 2280940

def test_mod1187_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1187_times_12800_plus_image_type_times_14700_plus_width_times_1460_plus_height_times_1430
    assert xcf_file_size_mod_1187_times_12800_plus_image_type_times_14700_plus_width_times_1460_plus_height_times_1430(str(RED)) == 2268490

def test_mod1187_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1187_times_12800_plus_image_type_times_14700_plus_width_times_1460_plus_height_times_1430
    assert xcf_file_size_mod_1187_times_12800_plus_image_type_times_14700_plus_width_times_1460_plus_height_times_1430(str(BLUE)) == 2281290

def test_mod1187_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1187_times_12800_plus_image_type_times_14700_plus_width_times_1460_plus_height_times_1430
    assert xcf_file_size_mod_1187_times_12800_plus_image_type_times_14700_plus_width_times_1460_plus_height_times_1430(str(GRAY)) == 2298880

def test_mod1181_positive():
    from xcf.xcf_analytics import xcf_file_size_mod_1181_times_12700_plus_image_type_times_14600_plus_width_times_1450_plus_height_times_1420
    assert xcf_file_size_mod_1181_times_12700_plus_image_type_times_14600_plus_width_times_1450_plus_height_times_1420(str(RED)) > 0

def test_mod1187_positive():
    from xcf.xcf_analytics import xcf_file_size_mod_1187_times_12800_plus_image_type_times_14700_plus_width_times_1460_plus_height_times_1430
    assert xcf_file_size_mod_1187_times_12800_plus_image_type_times_14700_plus_width_times_1460_plus_height_times_1430(str(RED)) > 0

def test_mod1181_neq_mod1187():
    from xcf.xcf_analytics import xcf_file_size_mod_1181_times_12700_plus_image_type_times_14600_plus_width_times_1450_plus_height_times_1420, xcf_file_size_mod_1187_times_12800_plus_image_type_times_14700_plus_width_times_1460_plus_height_times_1430
    assert xcf_file_size_mod_1181_times_12700_plus_image_type_times_14600_plus_width_times_1450_plus_height_times_1420(str(GRAY)) != xcf_file_size_mod_1187_times_12800_plus_image_type_times_14700_plus_width_times_1460_plus_height_times_1430(str(GRAY))

def test_mod1181_consistent():
    from xcf.xcf_analytics import xcf_file_size_mod_1181_times_12700_plus_image_type_times_14600_plus_width_times_1450_plus_height_times_1420
    assert xcf_file_size_mod_1181_times_12700_plus_image_type_times_14600_plus_width_times_1450_plus_height_times_1420(str(BLUE)) == xcf_file_size_mod_1181_times_12700_plus_image_type_times_14600_plus_width_times_1450_plus_height_times_1420(str(BLUE))
