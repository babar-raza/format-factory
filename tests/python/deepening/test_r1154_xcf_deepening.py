"""Sprint 600 XCF analytics deepening tests - primes 1231, 1237."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"

def test_mod1231_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1231_times_13500_plus_image_type_times_15400_plus_width_times_1530_plus_height_times_1500
    assert xcf_file_size_mod_1231_times_13500_plus_image_type_times_15400_plus_width_times_1530_plus_height_times_1500(str(RED)) == 2392530

def test_mod1231_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1231_times_13500_plus_image_type_times_15400_plus_width_times_1530_plus_height_times_1500
    assert xcf_file_size_mod_1231_times_13500_plus_image_type_times_15400_plus_width_times_1530_plus_height_times_1500(str(BLUE)) == 2406030

def test_mod1231_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1231_times_13500_plus_image_type_times_15400_plus_width_times_1530_plus_height_times_1500
    assert xcf_file_size_mod_1231_times_13500_plus_image_type_times_15400_plus_width_times_1530_plus_height_times_1500(str(GRAY)) == 2424460

def test_mod1237_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1237_times_13600_plus_image_type_times_15500_plus_width_times_1540_plus_height_times_1510
    assert xcf_file_size_mod_1237_times_13600_plus_image_type_times_15500_plus_width_times_1540_plus_height_times_1510(str(RED)) == 2410250

def test_mod1237_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1237_times_13600_plus_image_type_times_15500_plus_width_times_1540_plus_height_times_1510
    assert xcf_file_size_mod_1237_times_13600_plus_image_type_times_15500_plus_width_times_1540_plus_height_times_1510(str(BLUE)) == 2423850

def test_mod1237_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1237_times_13600_plus_image_type_times_15500_plus_width_times_1540_plus_height_times_1510
    assert xcf_file_size_mod_1237_times_13600_plus_image_type_times_15500_plus_width_times_1540_plus_height_times_1510(str(GRAY)) == 2442400

def test_mod1231_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1231_times_13500_plus_image_type_times_15400_plus_width_times_1530_plus_height_times_1500
    assert isinstance(xcf_file_size_mod_1231_times_13500_plus_image_type_times_15400_plus_width_times_1530_plus_height_times_1500(str(RED)), int)

def test_mod1231_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1231_times_13500_plus_image_type_times_15400_plus_width_times_1530_plus_height_times_1500
    assert xcf_file_size_mod_1231_times_13500_plus_image_type_times_15400_plus_width_times_1530_plus_height_times_1500(str(RED)) >= 0

def test_mod1231_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1231_times_13500_plus_image_type_times_15400_plus_width_times_1530_plus_height_times_1500
    fn2 = xcf_file_size_mod_1231_times_13500_plus_image_type_times_15400_plus_width_times_1530_plus_height_times_1500
    results = {fn2(str(RED)), fn2(str(BLUE)), fn2(str(GRAY))}
    assert len(results) == 3

def test_mod1231_importable_from_package():
    from xcf import xcf_file_size_mod_1231_times_13500_plus_image_type_times_15400_plus_width_times_1530_plus_height_times_1500
    assert callable(xcf_file_size_mod_1231_times_13500_plus_image_type_times_15400_plus_width_times_1530_plus_height_times_1500)

def test_mod1237_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1237_times_13600_plus_image_type_times_15500_plus_width_times_1540_plus_height_times_1510
    assert isinstance(xcf_file_size_mod_1237_times_13600_plus_image_type_times_15500_plus_width_times_1540_plus_height_times_1510(str(RED)), int)

def test_mod1237_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1237_times_13600_plus_image_type_times_15500_plus_width_times_1540_plus_height_times_1510
    assert xcf_file_size_mod_1237_times_13600_plus_image_type_times_15500_plus_width_times_1540_plus_height_times_1510(str(RED)) >= 0

def test_mod1237_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1237_times_13600_plus_image_type_times_15500_plus_width_times_1540_plus_height_times_1510
    fn2 = xcf_file_size_mod_1237_times_13600_plus_image_type_times_15500_plus_width_times_1540_plus_height_times_1510
    results = {fn2(str(RED)), fn2(str(BLUE)), fn2(str(GRAY))}
    assert len(results) == 3

def test_mod1237_importable_from_package():
    from xcf import xcf_file_size_mod_1237_times_13600_plus_image_type_times_15500_plus_width_times_1540_plus_height_times_1510
    assert callable(xcf_file_size_mod_1237_times_13600_plus_image_type_times_15500_plus_width_times_1540_plus_height_times_1510)
