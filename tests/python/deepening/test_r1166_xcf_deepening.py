"""Sprint 612 XCF analytics deepening tests - primes 1291, 1297."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1291_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1291_times_14300_plus_image_type_times_16200_plus_width_times_1610_plus_height_times_1580
    assert xcf_file_size_mod_1291_times_14300_plus_image_type_times_16200_plus_width_times_1610_plus_height_times_1580(str(RED)) == 2534290


def test_mod1291_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1291_times_14300_plus_image_type_times_16200_plus_width_times_1610_plus_height_times_1580
    assert xcf_file_size_mod_1291_times_14300_plus_image_type_times_16200_plus_width_times_1610_plus_height_times_1580(str(BLUE)) == 2548590


def test_mod1291_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1291_times_14300_plus_image_type_times_16200_plus_width_times_1610_plus_height_times_1580
    assert xcf_file_size_mod_1291_times_14300_plus_image_type_times_16200_plus_width_times_1610_plus_height_times_1580(str(GRAY)) == 2567980


def test_mod1297_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1297_times_14400_plus_image_type_times_16300_plus_width_times_1620_plus_height_times_1590
    assert xcf_file_size_mod_1297_times_14400_plus_image_type_times_16300_plus_width_times_1620_plus_height_times_1590(str(RED)) == 2552010


def test_mod1297_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1297_times_14400_plus_image_type_times_16300_plus_width_times_1620_plus_height_times_1590
    assert xcf_file_size_mod_1297_times_14400_plus_image_type_times_16300_plus_width_times_1620_plus_height_times_1590(str(BLUE)) == 2566410


def test_mod1297_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1297_times_14400_plus_image_type_times_16300_plus_width_times_1620_plus_height_times_1590
    assert xcf_file_size_mod_1297_times_14400_plus_image_type_times_16300_plus_width_times_1620_plus_height_times_1590(str(GRAY)) == 2585920


def test_mod1291_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1291_times_14300_plus_image_type_times_16200_plus_width_times_1610_plus_height_times_1580
    assert isinstance(xcf_file_size_mod_1291_times_14300_plus_image_type_times_16200_plus_width_times_1610_plus_height_times_1580(str(RED)), int)


def test_mod1297_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1297_times_14400_plus_image_type_times_16300_plus_width_times_1620_plus_height_times_1590
    assert isinstance(xcf_file_size_mod_1297_times_14400_plus_image_type_times_16300_plus_width_times_1620_plus_height_times_1590(str(RED)), int)


def test_mod1291_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1291_times_14300_plus_image_type_times_16200_plus_width_times_1610_plus_height_times_1580
    assert xcf_file_size_mod_1291_times_14300_plus_image_type_times_16200_plus_width_times_1610_plus_height_times_1580(str(RED)) >= 0


def test_mod1297_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1297_times_14400_plus_image_type_times_16300_plus_width_times_1620_plus_height_times_1590
    assert xcf_file_size_mod_1297_times_14400_plus_image_type_times_16300_plus_width_times_1620_plus_height_times_1590(str(RED)) >= 0


def test_mod1291_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1291_times_14300_plus_image_type_times_16200_plus_width_times_1610_plus_height_times_1580
    fn = xcf_file_size_mod_1291_times_14300_plus_image_type_times_16200_plus_width_times_1610_plus_height_times_1580
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1297_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1297_times_14400_plus_image_type_times_16300_plus_width_times_1620_plus_height_times_1590
    fn = xcf_file_size_mod_1297_times_14400_plus_image_type_times_16300_plus_width_times_1620_plus_height_times_1590
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1291_importable_from_package():
    from xcf import xcf_file_size_mod_1291_times_14300_plus_image_type_times_16200_plus_width_times_1610_plus_height_times_1580
    assert callable(xcf_file_size_mod_1291_times_14300_plus_image_type_times_16200_plus_width_times_1610_plus_height_times_1580)


def test_mod1297_importable_from_package():
    from xcf import xcf_file_size_mod_1297_times_14400_plus_image_type_times_16300_plus_width_times_1620_plus_height_times_1590
    assert callable(xcf_file_size_mod_1297_times_14400_plus_image_type_times_16300_plus_width_times_1620_plus_height_times_1590)
