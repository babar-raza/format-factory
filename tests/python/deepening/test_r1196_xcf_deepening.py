"""Sprint 642 XCF analytics deepening tests - primes 1451, 1453."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1451_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1451_times_16300_plus_image_type_times_18200_plus_width_times_1810_plus_height_times_1780
    assert xcf_file_size_mod_1451_times_16300_plus_image_type_times_18200_plus_width_times_1810_plus_height_times_1780(str(RED)) == 2888690


def test_mod1451_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1451_times_16300_plus_image_type_times_18200_plus_width_times_1810_plus_height_times_1780
    assert xcf_file_size_mod_1451_times_16300_plus_image_type_times_18200_plus_width_times_1810_plus_height_times_1780(str(BLUE)) == 2904990


def test_mod1451_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1451_times_16300_plus_image_type_times_18200_plus_width_times_1810_plus_height_times_1780
    assert xcf_file_size_mod_1451_times_16300_plus_image_type_times_18200_plus_width_times_1810_plus_height_times_1780(str(GRAY)) == 2926780


def test_mod1453_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1453_times_16400_plus_image_type_times_18300_plus_width_times_1820_plus_height_times_1790
    assert xcf_file_size_mod_1453_times_16400_plus_image_type_times_18300_plus_width_times_1820_plus_height_times_1790(str(RED)) == 2906410


def test_mod1453_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1453_times_16400_plus_image_type_times_18300_plus_width_times_1820_plus_height_times_1790
    assert xcf_file_size_mod_1453_times_16400_plus_image_type_times_18300_plus_width_times_1820_plus_height_times_1790(str(BLUE)) == 2922810


def test_mod1453_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1453_times_16400_plus_image_type_times_18300_plus_width_times_1820_plus_height_times_1790
    assert xcf_file_size_mod_1453_times_16400_plus_image_type_times_18300_plus_width_times_1820_plus_height_times_1790(str(GRAY)) == 2944720


def test_mod1451_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1451_times_16300_plus_image_type_times_18200_plus_width_times_1810_plus_height_times_1780
    assert isinstance(xcf_file_size_mod_1451_times_16300_plus_image_type_times_18200_plus_width_times_1810_plus_height_times_1780(str(RED)), int)


def test_mod1453_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1453_times_16400_plus_image_type_times_18300_plus_width_times_1820_plus_height_times_1790
    assert isinstance(xcf_file_size_mod_1453_times_16400_plus_image_type_times_18300_plus_width_times_1820_plus_height_times_1790(str(RED)), int)


def test_mod1451_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1451_times_16300_plus_image_type_times_18200_plus_width_times_1810_plus_height_times_1780
    assert xcf_file_size_mod_1451_times_16300_plus_image_type_times_18200_plus_width_times_1810_plus_height_times_1780(str(RED)) >= 0


def test_mod1453_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1453_times_16400_plus_image_type_times_18300_plus_width_times_1820_plus_height_times_1790
    assert xcf_file_size_mod_1453_times_16400_plus_image_type_times_18300_plus_width_times_1820_plus_height_times_1790(str(RED)) >= 0


def test_mod1451_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1451_times_16300_plus_image_type_times_18200_plus_width_times_1810_plus_height_times_1780
    fn = xcf_file_size_mod_1451_times_16300_plus_image_type_times_18200_plus_width_times_1810_plus_height_times_1780
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1453_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1453_times_16400_plus_image_type_times_18300_plus_width_times_1820_plus_height_times_1790
    fn = xcf_file_size_mod_1453_times_16400_plus_image_type_times_18300_plus_width_times_1820_plus_height_times_1790
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1451_importable_from_package():
    from xcf import xcf_file_size_mod_1451_times_16300_plus_image_type_times_18200_plus_width_times_1810_plus_height_times_1780
    assert callable(xcf_file_size_mod_1451_times_16300_plus_image_type_times_18200_plus_width_times_1810_plus_height_times_1780)


def test_mod1453_importable_from_package():
    from xcf import xcf_file_size_mod_1453_times_16400_plus_image_type_times_18300_plus_width_times_1820_plus_height_times_1790
    assert callable(xcf_file_size_mod_1453_times_16400_plus_image_type_times_18300_plus_width_times_1820_plus_height_times_1790)
