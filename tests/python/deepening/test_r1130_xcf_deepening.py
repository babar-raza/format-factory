"""Sprint 576 XCF analytics deepening tests - primes 1109, 1117."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"

def test_mod1109_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1109_times_11900_plus_image_type_times_13800_plus_width_times_1370_plus_height_times_1340
    assert xcf_file_size_mod_1109_times_11900_plus_image_type_times_13800_plus_width_times_1370_plus_height_times_1340(str(RED)) == 2109010

def test_mod1109_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1109_times_11900_plus_image_type_times_13800_plus_width_times_1370_plus_height_times_1340
    assert xcf_file_size_mod_1109_times_11900_plus_image_type_times_13800_plus_width_times_1370_plus_height_times_1340(str(BLUE)) == 2120910

def test_mod1109_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1109_times_11900_plus_image_type_times_13800_plus_width_times_1370_plus_height_times_1340
    assert xcf_file_size_mod_1109_times_11900_plus_image_type_times_13800_plus_width_times_1370_plus_height_times_1340(str(GRAY)) == 2137420

def test_mod1117_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1117_times_12000_plus_image_type_times_13900_plus_width_times_1380_plus_height_times_1350
    assert xcf_file_size_mod_1117_times_12000_plus_image_type_times_13900_plus_width_times_1380_plus_height_times_1350(str(RED)) == 2126730

def test_mod1117_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1117_times_12000_plus_image_type_times_13900_plus_width_times_1380_plus_height_times_1350
    assert xcf_file_size_mod_1117_times_12000_plus_image_type_times_13900_plus_width_times_1380_plus_height_times_1350(str(BLUE)) == 2138730

def test_mod1117_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1117_times_12000_plus_image_type_times_13900_plus_width_times_1380_plus_height_times_1350
    assert xcf_file_size_mod_1117_times_12000_plus_image_type_times_13900_plus_width_times_1380_plus_height_times_1350(str(GRAY)) == 2155360

def test_mod1109_red_positive():
    from xcf.xcf_analytics import xcf_file_size_mod_1109_times_11900_plus_image_type_times_13800_plus_width_times_1370_plus_height_times_1340
    assert xcf_file_size_mod_1109_times_11900_plus_image_type_times_13800_plus_width_times_1370_plus_height_times_1340(str(RED)) > 0

def test_mod1117_red_positive():
    from xcf.xcf_analytics import xcf_file_size_mod_1117_times_12000_plus_image_type_times_13900_plus_width_times_1380_plus_height_times_1350
    assert xcf_file_size_mod_1117_times_12000_plus_image_type_times_13900_plus_width_times_1380_plus_height_times_1350(str(RED)) > 0

def test_mod1109_neq_mod1117_gray():
    from xcf.xcf_analytics import (
        xcf_file_size_mod_1109_times_11900_plus_image_type_times_13800_plus_width_times_1370_plus_height_times_1340,
        xcf_file_size_mod_1117_times_12000_plus_image_type_times_13900_plus_width_times_1380_plus_height_times_1350,
    )
    assert xcf_file_size_mod_1109_times_11900_plus_image_type_times_13800_plus_width_times_1370_plus_height_times_1340(str(GRAY)) != xcf_file_size_mod_1117_times_12000_plus_image_type_times_13900_plus_width_times_1380_plus_height_times_1350(str(GRAY))

def test_mod1109_consistent():
    from xcf.xcf_analytics import xcf_file_size_mod_1109_times_11900_plus_image_type_times_13800_plus_width_times_1370_plus_height_times_1340
    assert xcf_file_size_mod_1109_times_11900_plus_image_type_times_13800_plus_width_times_1370_plus_height_times_1340(str(BLUE)) == xcf_file_size_mod_1109_times_11900_plus_image_type_times_13800_plus_width_times_1370_plus_height_times_1340(str(BLUE))
