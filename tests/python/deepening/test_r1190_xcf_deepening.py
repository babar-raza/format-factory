"""Sprint 636 XCF analytics deepening tests - primes 1429, 1433."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1429_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1429_times_15900_plus_image_type_times_17800_plus_width_times_1770_plus_height_times_1740
    assert xcf_file_size_mod_1429_times_15900_plus_image_type_times_17800_plus_width_times_1770_plus_height_times_1740(str(RED)) == 2817810


def test_mod1429_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1429_times_15900_plus_image_type_times_17800_plus_width_times_1770_plus_height_times_1740
    assert xcf_file_size_mod_1429_times_15900_plus_image_type_times_17800_plus_width_times_1770_plus_height_times_1740(str(BLUE)) == 2833710


def test_mod1429_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1429_times_15900_plus_image_type_times_17800_plus_width_times_1770_plus_height_times_1740
    assert xcf_file_size_mod_1429_times_15900_plus_image_type_times_17800_plus_width_times_1770_plus_height_times_1740(str(GRAY)) == 2855020


def test_mod1429_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1429_times_15900_plus_image_type_times_17800_plus_width_times_1770_plus_height_times_1740
    assert isinstance(xcf_file_size_mod_1429_times_15900_plus_image_type_times_17800_plus_width_times_1770_plus_height_times_1740(str(RED)), int)


def test_mod1429_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1429_times_15900_plus_image_type_times_17800_plus_width_times_1770_plus_height_times_1740
    assert xcf_file_size_mod_1429_times_15900_plus_image_type_times_17800_plus_width_times_1770_plus_height_times_1740(str(RED)) >= 0


def test_mod1429_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1429_times_15900_plus_image_type_times_17800_plus_width_times_1770_plus_height_times_1740
    fn_ref = xcf_file_size_mod_1429_times_15900_plus_image_type_times_17800_plus_width_times_1770_plus_height_times_1740
    results = {fn_ref(str(RED)), fn_ref(str(BLUE)), fn_ref(str(GRAY))}
    assert len(results) == 3


def test_mod1429_importable_from_package():
    from xcf import xcf_file_size_mod_1429_times_15900_plus_image_type_times_17800_plus_width_times_1770_plus_height_times_1740
    assert callable(xcf_file_size_mod_1429_times_15900_plus_image_type_times_17800_plus_width_times_1770_plus_height_times_1740)


def test_mod1433_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1433_times_16000_plus_image_type_times_17900_plus_width_times_1780_plus_height_times_1750
    assert xcf_file_size_mod_1433_times_16000_plus_image_type_times_17900_plus_width_times_1780_plus_height_times_1750(str(RED)) == 2835530


def test_mod1433_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1433_times_16000_plus_image_type_times_17900_plus_width_times_1780_plus_height_times_1750
    assert xcf_file_size_mod_1433_times_16000_plus_image_type_times_17900_plus_width_times_1780_plus_height_times_1750(str(BLUE)) == 2851530


def test_mod1433_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1433_times_16000_plus_image_type_times_17900_plus_width_times_1780_plus_height_times_1750
    assert xcf_file_size_mod_1433_times_16000_plus_image_type_times_17900_plus_width_times_1780_plus_height_times_1750(str(GRAY)) == 2872960


def test_mod1433_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1433_times_16000_plus_image_type_times_17900_plus_width_times_1780_plus_height_times_1750
    assert isinstance(xcf_file_size_mod_1433_times_16000_plus_image_type_times_17900_plus_width_times_1780_plus_height_times_1750(str(RED)), int)


def test_mod1433_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1433_times_16000_plus_image_type_times_17900_plus_width_times_1780_plus_height_times_1750
    assert xcf_file_size_mod_1433_times_16000_plus_image_type_times_17900_plus_width_times_1780_plus_height_times_1750(str(RED)) >= 0


def test_mod1433_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1433_times_16000_plus_image_type_times_17900_plus_width_times_1780_plus_height_times_1750
    fn_ref = xcf_file_size_mod_1433_times_16000_plus_image_type_times_17900_plus_width_times_1780_plus_height_times_1750
    results = {fn_ref(str(RED)), fn_ref(str(BLUE)), fn_ref(str(GRAY))}
    assert len(results) == 3


def test_mod1433_importable_from_package():
    from xcf import xcf_file_size_mod_1433_times_16000_plus_image_type_times_17900_plus_width_times_1780_plus_height_times_1750
    assert callable(xcf_file_size_mod_1433_times_16000_plus_image_type_times_17900_plus_width_times_1780_plus_height_times_1750)
