"""Sprint 573 XCF analytics deepening tests - primes 1097, 1103."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"

def test_mod1097_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1097_times_11700_plus_image_type_times_13600_plus_width_times_1350_plus_height_times_1320
    assert xcf_file_size_mod_1097_times_11700_plus_image_type_times_13600_plus_width_times_1350_plus_height_times_1320(str(RED)) == 2073570

def test_mod1097_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1097_times_11700_plus_image_type_times_13600_plus_width_times_1350_plus_height_times_1320
    assert xcf_file_size_mod_1097_times_11700_plus_image_type_times_13600_plus_width_times_1350_plus_height_times_1320(str(BLUE)) == 2085270

def test_mod1097_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1097_times_11700_plus_image_type_times_13600_plus_width_times_1350_plus_height_times_1320
    assert xcf_file_size_mod_1097_times_11700_plus_image_type_times_13600_plus_width_times_1350_plus_height_times_1320(str(GRAY)) == 2101540

def test_mod1103_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1103_times_11800_plus_image_type_times_13700_plus_width_times_1360_plus_height_times_1330
    assert xcf_file_size_mod_1103_times_11800_plus_image_type_times_13700_plus_width_times_1360_plus_height_times_1330(str(RED)) == 2091290

def test_mod1103_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1103_times_11800_plus_image_type_times_13700_plus_width_times_1360_plus_height_times_1330
    assert xcf_file_size_mod_1103_times_11800_plus_image_type_times_13700_plus_width_times_1360_plus_height_times_1330(str(BLUE)) == 2103090

def test_mod1103_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1103_times_11800_plus_image_type_times_13700_plus_width_times_1360_plus_height_times_1330
    assert xcf_file_size_mod_1103_times_11800_plus_image_type_times_13700_plus_width_times_1360_plus_height_times_1330(str(GRAY)) == 2119480

def test_mod1097_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1097_times_11700_plus_image_type_times_13600_plus_width_times_1350_plus_height_times_1320
    assert isinstance(xcf_file_size_mod_1097_times_11700_plus_image_type_times_13600_plus_width_times_1350_plus_height_times_1320(str(RED)), int)

def test_mod1097_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1097_times_11700_plus_image_type_times_13600_plus_width_times_1350_plus_height_times_1320
    assert xcf_file_size_mod_1097_times_11700_plus_image_type_times_13600_plus_width_times_1350_plus_height_times_1320(str(RED)) >= 0

def test_mod1097_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1097_times_11700_plus_image_type_times_13600_plus_width_times_1350_plus_height_times_1320
    f=xcf_file_size_mod_1097_times_11700_plus_image_type_times_13600_plus_width_times_1350_plus_height_times_1320
    assert len({f(str(RED)),f(str(BLUE)),f(str(GRAY))})==3

def test_mod1097_importable_from_package():
    from xcf import xcf_file_size_mod_1097_times_11700_plus_image_type_times_13600_plus_width_times_1350_plus_height_times_1320
    assert callable(xcf_file_size_mod_1097_times_11700_plus_image_type_times_13600_plus_width_times_1350_plus_height_times_1320)

def test_mod1103_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1103_times_11800_plus_image_type_times_13700_plus_width_times_1360_plus_height_times_1330
    assert isinstance(xcf_file_size_mod_1103_times_11800_plus_image_type_times_13700_plus_width_times_1360_plus_height_times_1330(str(RED)), int)

def test_mod1103_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1103_times_11800_plus_image_type_times_13700_plus_width_times_1360_plus_height_times_1330
    assert xcf_file_size_mod_1103_times_11800_plus_image_type_times_13700_plus_width_times_1360_plus_height_times_1330(str(RED)) >= 0

def test_mod1103_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1103_times_11800_plus_image_type_times_13700_plus_width_times_1360_plus_height_times_1330
    f=xcf_file_size_mod_1103_times_11800_plus_image_type_times_13700_plus_width_times_1360_plus_height_times_1330
    assert len({f(str(RED)),f(str(BLUE)),f(str(GRAY))})==3

def test_mod1103_importable_from_package():
    from xcf import xcf_file_size_mod_1103_times_11800_plus_image_type_times_13700_plus_width_times_1360_plus_height_times_1330
    assert callable(xcf_file_size_mod_1103_times_11800_plus_image_type_times_13700_plus_width_times_1360_plus_height_times_1330)
