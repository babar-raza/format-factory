"""Sprint 597 XCF analytics deepening tests - primes 1223, 1229."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"

def test_mod1223_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1223_times_13300_plus_image_type_times_15200_plus_width_times_1510_plus_height_times_1480
    assert xcf_file_size_mod_1223_times_13300_plus_image_type_times_15200_plus_width_times_1510_plus_height_times_1480(str(RED)) == 2357090

def test_mod1223_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1223_times_13300_plus_image_type_times_15200_plus_width_times_1510_plus_height_times_1480
    assert xcf_file_size_mod_1223_times_13300_plus_image_type_times_15200_plus_width_times_1510_plus_height_times_1480(str(BLUE)) == 2370390

def test_mod1223_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1223_times_13300_plus_image_type_times_15200_plus_width_times_1510_plus_height_times_1480
    assert xcf_file_size_mod_1223_times_13300_plus_image_type_times_15200_plus_width_times_1510_plus_height_times_1480(str(GRAY)) == 2388580

def test_mod1229_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1229_times_13400_plus_image_type_times_15300_plus_width_times_1520_plus_height_times_1490
    assert xcf_file_size_mod_1229_times_13400_plus_image_type_times_15300_plus_width_times_1520_plus_height_times_1490(str(RED)) == 2374810

def test_mod1229_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1229_times_13400_plus_image_type_times_15300_plus_width_times_1520_plus_height_times_1490
    assert xcf_file_size_mod_1229_times_13400_plus_image_type_times_15300_plus_width_times_1520_plus_height_times_1490(str(BLUE)) == 2388210

def test_mod1229_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1229_times_13400_plus_image_type_times_15300_plus_width_times_1520_plus_height_times_1490
    assert xcf_file_size_mod_1229_times_13400_plus_image_type_times_15300_plus_width_times_1520_plus_height_times_1490(str(GRAY)) == 2406520

def test_mod1223_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1223_times_13300_plus_image_type_times_15200_plus_width_times_1510_plus_height_times_1480
    assert isinstance(xcf_file_size_mod_1223_times_13300_plus_image_type_times_15200_plus_width_times_1510_plus_height_times_1480(str(RED)), int)

def test_mod1223_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1223_times_13300_plus_image_type_times_15200_plus_width_times_1510_plus_height_times_1480
    assert xcf_file_size_mod_1223_times_13300_plus_image_type_times_15200_plus_width_times_1510_plus_height_times_1480(str(RED)) >= 0

def test_mod1223_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1223_times_13300_plus_image_type_times_15200_plus_width_times_1510_plus_height_times_1480
    fn2 = xcf_file_size_mod_1223_times_13300_plus_image_type_times_15200_plus_width_times_1510_plus_height_times_1480
    results = {fn2(str(RED)), fn2(str(BLUE)), fn2(str(GRAY))}
    assert len(results) == 3

def test_mod1223_importable_from_package():
    from xcf import xcf_file_size_mod_1223_times_13300_plus_image_type_times_15200_plus_width_times_1510_plus_height_times_1480
    assert callable(xcf_file_size_mod_1223_times_13300_plus_image_type_times_15200_plus_width_times_1510_plus_height_times_1480)

def test_mod1229_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1229_times_13400_plus_image_type_times_15300_plus_width_times_1520_plus_height_times_1490
    assert isinstance(xcf_file_size_mod_1229_times_13400_plus_image_type_times_15300_plus_width_times_1520_plus_height_times_1490(str(RED)), int)

def test_mod1229_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1229_times_13400_plus_image_type_times_15300_plus_width_times_1520_plus_height_times_1490
    assert xcf_file_size_mod_1229_times_13400_plus_image_type_times_15300_plus_width_times_1520_plus_height_times_1490(str(RED)) >= 0

def test_mod1229_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1229_times_13400_plus_image_type_times_15300_plus_width_times_1520_plus_height_times_1490
    fn2 = xcf_file_size_mod_1229_times_13400_plus_image_type_times_15300_plus_width_times_1520_plus_height_times_1490
    results = {fn2(str(RED)), fn2(str(BLUE)), fn2(str(GRAY))}
    assert len(results) == 3

def test_mod1229_importable_from_package():
    from xcf import xcf_file_size_mod_1229_times_13400_plus_image_type_times_15300_plus_width_times_1520_plus_height_times_1490
    assert callable(xcf_file_size_mod_1229_times_13400_plus_image_type_times_15300_plus_width_times_1520_plus_height_times_1490)
