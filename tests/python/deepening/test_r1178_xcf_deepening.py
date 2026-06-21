"""Sprint 624 XCF analytics deepening tests - primes 1361, 1367."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1361_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1361_times_15100_plus_image_type_times_17000_plus_width_times_1690_plus_height_times_1660
    assert xcf_file_size_mod_1361_times_15100_plus_image_type_times_17000_plus_width_times_1690_plus_height_times_1660(str(RED)) == 2676050


def test_mod1361_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1361_times_15100_plus_image_type_times_17000_plus_width_times_1690_plus_height_times_1660
    assert xcf_file_size_mod_1361_times_15100_plus_image_type_times_17000_plus_width_times_1690_plus_height_times_1660(str(BLUE)) == 2691150


def test_mod1361_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1361_times_15100_plus_image_type_times_17000_plus_width_times_1690_plus_height_times_1660
    assert xcf_file_size_mod_1361_times_15100_plus_image_type_times_17000_plus_width_times_1690_plus_height_times_1660(str(GRAY)) == 2711500


def test_mod1367_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1367_times_15200_plus_image_type_times_17100_plus_width_times_1700_plus_height_times_1670
    assert xcf_file_size_mod_1367_times_15200_plus_image_type_times_17100_plus_width_times_1700_plus_height_times_1670(str(RED)) == 2693770


def test_mod1367_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1367_times_15200_plus_image_type_times_17100_plus_width_times_1700_plus_height_times_1670
    assert xcf_file_size_mod_1367_times_15200_plus_image_type_times_17100_plus_width_times_1700_plus_height_times_1670(str(BLUE)) == 2708970


def test_mod1367_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1367_times_15200_plus_image_type_times_17100_plus_width_times_1700_plus_height_times_1670
    assert xcf_file_size_mod_1367_times_15200_plus_image_type_times_17100_plus_width_times_1700_plus_height_times_1670(str(GRAY)) == 2729440


def test_mod1361_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1361_times_15100_plus_image_type_times_17000_plus_width_times_1690_plus_height_times_1660
    assert isinstance(xcf_file_size_mod_1361_times_15100_plus_image_type_times_17000_plus_width_times_1690_plus_height_times_1660(str(RED)), int)


def test_mod1367_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1367_times_15200_plus_image_type_times_17100_plus_width_times_1700_plus_height_times_1670
    assert isinstance(xcf_file_size_mod_1367_times_15200_plus_image_type_times_17100_plus_width_times_1700_plus_height_times_1670(str(RED)), int)


def test_mod1361_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1361_times_15100_plus_image_type_times_17000_plus_width_times_1690_plus_height_times_1660
    assert xcf_file_size_mod_1361_times_15100_plus_image_type_times_17000_plus_width_times_1690_plus_height_times_1660(str(RED)) >= 0


def test_mod1367_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1367_times_15200_plus_image_type_times_17100_plus_width_times_1700_plus_height_times_1670
    assert xcf_file_size_mod_1367_times_15200_plus_image_type_times_17100_plus_width_times_1700_plus_height_times_1670(str(RED)) >= 0


def test_mod1361_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1361_times_15100_plus_image_type_times_17000_plus_width_times_1690_plus_height_times_1660
    fn = xcf_file_size_mod_1361_times_15100_plus_image_type_times_17000_plus_width_times_1690_plus_height_times_1660
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1367_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1367_times_15200_plus_image_type_times_17100_plus_width_times_1700_plus_height_times_1670
    fn = xcf_file_size_mod_1367_times_15200_plus_image_type_times_17100_plus_width_times_1700_plus_height_times_1670
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1361_importable_from_package():
    from xcf import xcf_file_size_mod_1361_times_15100_plus_image_type_times_17000_plus_width_times_1690_plus_height_times_1660
    assert callable(xcf_file_size_mod_1361_times_15100_plus_image_type_times_17000_plus_width_times_1690_plus_height_times_1660)


def test_mod1367_importable_from_package():
    from xcf import xcf_file_size_mod_1367_times_15200_plus_image_type_times_17100_plus_width_times_1700_plus_height_times_1670
    assert callable(xcf_file_size_mod_1367_times_15200_plus_image_type_times_17100_plus_width_times_1700_plus_height_times_1670)
