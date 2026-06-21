"""Sprint 627 XCF analytics deepening tests - primes 1373, 1381."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1373_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1373_times_15300_plus_image_type_times_17200_plus_width_times_1710_plus_height_times_1680
    assert xcf_file_size_mod_1373_times_15300_plus_image_type_times_17200_plus_width_times_1710_plus_height_times_1680(str(RED)) == 2711490


def test_mod1373_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1373_times_15300_plus_image_type_times_17200_plus_width_times_1710_plus_height_times_1680
    assert xcf_file_size_mod_1373_times_15300_plus_image_type_times_17200_plus_width_times_1710_plus_height_times_1680(str(BLUE)) == 2726790


def test_mod1373_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1373_times_15300_plus_image_type_times_17200_plus_width_times_1710_plus_height_times_1680
    assert xcf_file_size_mod_1373_times_15300_plus_image_type_times_17200_plus_width_times_1710_plus_height_times_1680(str(GRAY)) == 2747380


def test_mod1381_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1381_times_15400_plus_image_type_times_17300_plus_width_times_1720_plus_height_times_1690
    assert xcf_file_size_mod_1381_times_15400_plus_image_type_times_17300_plus_width_times_1720_plus_height_times_1690(str(RED)) == 2729210


def test_mod1381_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1381_times_15400_plus_image_type_times_17300_plus_width_times_1720_plus_height_times_1690
    assert xcf_file_size_mod_1381_times_15400_plus_image_type_times_17300_plus_width_times_1720_plus_height_times_1690(str(BLUE)) == 2744610


def test_mod1381_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1381_times_15400_plus_image_type_times_17300_plus_width_times_1720_plus_height_times_1690
    assert xcf_file_size_mod_1381_times_15400_plus_image_type_times_17300_plus_width_times_1720_plus_height_times_1690(str(GRAY)) == 2765320


def test_mod1373_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1373_times_15300_plus_image_type_times_17200_plus_width_times_1710_plus_height_times_1680
    assert isinstance(xcf_file_size_mod_1373_times_15300_plus_image_type_times_17200_plus_width_times_1710_plus_height_times_1680(str(RED)), int)


def test_mod1381_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1381_times_15400_plus_image_type_times_17300_plus_width_times_1720_plus_height_times_1690
    assert isinstance(xcf_file_size_mod_1381_times_15400_plus_image_type_times_17300_plus_width_times_1720_plus_height_times_1690(str(RED)), int)


def test_mod1373_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1373_times_15300_plus_image_type_times_17200_plus_width_times_1710_plus_height_times_1680
    assert xcf_file_size_mod_1373_times_15300_plus_image_type_times_17200_plus_width_times_1710_plus_height_times_1680(str(RED)) >= 0


def test_mod1381_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1381_times_15400_plus_image_type_times_17300_plus_width_times_1720_plus_height_times_1690
    assert xcf_file_size_mod_1381_times_15400_plus_image_type_times_17300_plus_width_times_1720_plus_height_times_1690(str(RED)) >= 0


def test_mod1373_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1373_times_15300_plus_image_type_times_17200_plus_width_times_1710_plus_height_times_1680
    fn = xcf_file_size_mod_1373_times_15300_plus_image_type_times_17200_plus_width_times_1710_plus_height_times_1680
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1381_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1381_times_15400_plus_image_type_times_17300_plus_width_times_1720_plus_height_times_1690
    fn = xcf_file_size_mod_1381_times_15400_plus_image_type_times_17300_plus_width_times_1720_plus_height_times_1690
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1373_importable_from_package():
    from xcf import xcf_file_size_mod_1373_times_15300_plus_image_type_times_17200_plus_width_times_1710_plus_height_times_1680
    assert callable(xcf_file_size_mod_1373_times_15300_plus_image_type_times_17200_plus_width_times_1710_plus_height_times_1680)


def test_mod1381_importable_from_package():
    from xcf import xcf_file_size_mod_1381_times_15400_plus_image_type_times_17300_plus_width_times_1720_plus_height_times_1690
    assert callable(xcf_file_size_mod_1381_times_15400_plus_image_type_times_17300_plus_width_times_1720_plus_height_times_1690)
