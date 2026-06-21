"""Sprint 570 XCF analytics deepening tests - primes 1091, 1093."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"

def test_mod1091_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1091_times_11500_plus_image_type_times_13400_plus_width_times_1330_plus_height_times_1300
    assert xcf_file_size_mod_1091_times_11500_plus_image_type_times_13400_plus_width_times_1330_plus_height_times_1300(str(RED)) == 2038130

def test_mod1091_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1091_times_11500_plus_image_type_times_13400_plus_width_times_1330_plus_height_times_1300
    assert xcf_file_size_mod_1091_times_11500_plus_image_type_times_13400_plus_width_times_1330_plus_height_times_1300(str(BLUE)) == 2049630

def test_mod1091_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1091_times_11500_plus_image_type_times_13400_plus_width_times_1330_plus_height_times_1300
    assert xcf_file_size_mod_1091_times_11500_plus_image_type_times_13400_plus_width_times_1330_plus_height_times_1300(str(GRAY)) == 2065660

def test_mod1093_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1093_times_11600_plus_image_type_times_13500_plus_width_times_1340_plus_height_times_1310
    assert xcf_file_size_mod_1093_times_11600_plus_image_type_times_13500_plus_width_times_1340_plus_height_times_1310(str(RED)) == 2055850

def test_mod1093_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1093_times_11600_plus_image_type_times_13500_plus_width_times_1340_plus_height_times_1310
    assert xcf_file_size_mod_1093_times_11600_plus_image_type_times_13500_plus_width_times_1340_plus_height_times_1310(str(BLUE)) == 2067450

def test_mod1093_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1093_times_11600_plus_image_type_times_13500_plus_width_times_1340_plus_height_times_1310
    assert xcf_file_size_mod_1093_times_11600_plus_image_type_times_13500_plus_width_times_1340_plus_height_times_1310(str(GRAY)) == 2083600

def test_mod1091_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1091_times_11500_plus_image_type_times_13400_plus_width_times_1330_plus_height_times_1300
    assert isinstance(xcf_file_size_mod_1091_times_11500_plus_image_type_times_13400_plus_width_times_1330_plus_height_times_1300(str(RED)), int)

def test_mod1091_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1091_times_11500_plus_image_type_times_13400_plus_width_times_1330_plus_height_times_1300
    assert xcf_file_size_mod_1091_times_11500_plus_image_type_times_13400_plus_width_times_1330_plus_height_times_1300(str(RED)) >= 0

def test_mod1091_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1091_times_11500_plus_image_type_times_13400_plus_width_times_1330_plus_height_times_1300
    fn2 = xcf_file_size_mod_1091_times_11500_plus_image_type_times_13400_plus_width_times_1330_plus_height_times_1300
    results = {fn2(str(RED)), fn2(str(BLUE)), fn2(str(GRAY))}
    assert len(results) == 3

def test_mod1091_importable_from_package():
    from xcf import xcf_file_size_mod_1091_times_11500_plus_image_type_times_13400_plus_width_times_1330_plus_height_times_1300
    assert callable(xcf_file_size_mod_1091_times_11500_plus_image_type_times_13400_plus_width_times_1330_plus_height_times_1300)

def test_mod1093_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1093_times_11600_plus_image_type_times_13500_plus_width_times_1340_plus_height_times_1310
    assert isinstance(xcf_file_size_mod_1093_times_11600_plus_image_type_times_13500_plus_width_times_1340_plus_height_times_1310(str(RED)), int)

def test_mod1093_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1093_times_11600_plus_image_type_times_13500_plus_width_times_1340_plus_height_times_1310
    assert xcf_file_size_mod_1093_times_11600_plus_image_type_times_13500_plus_width_times_1340_plus_height_times_1310(str(RED)) >= 0

def test_mod1093_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1093_times_11600_plus_image_type_times_13500_plus_width_times_1340_plus_height_times_1310
    fn2 = xcf_file_size_mod_1093_times_11600_plus_image_type_times_13500_plus_width_times_1340_plus_height_times_1310
    results = {fn2(str(RED)), fn2(str(BLUE)), fn2(str(GRAY))}
    assert len(results) == 3

def test_mod1093_importable_from_package():
    from xcf import xcf_file_size_mod_1093_times_11600_plus_image_type_times_13500_plus_width_times_1340_plus_height_times_1310
    assert callable(xcf_file_size_mod_1093_times_11600_plus_image_type_times_13500_plus_width_times_1340_plus_height_times_1310)
