"""Sprint 561 XCF analytics deepening tests - primes 1049, 1051."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1049_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1049_times_10900_plus_image_type_times_12800_plus_width_times_1270_plus_height_times_1240
    assert xcf_file_size_mod_1049_times_10900_plus_image_type_times_12800_plus_width_times_1270_plus_height_times_1240(str(RED)) == 1931810


def test_mod1049_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1049_times_10900_plus_image_type_times_12800_plus_width_times_1270_plus_height_times_1240
    assert xcf_file_size_mod_1049_times_10900_plus_image_type_times_12800_plus_width_times_1270_plus_height_times_1240(str(BLUE)) == 1942710


def test_mod1049_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1049_times_10900_plus_image_type_times_12800_plus_width_times_1270_plus_height_times_1240
    assert xcf_file_size_mod_1049_times_10900_plus_image_type_times_12800_plus_width_times_1270_plus_height_times_1240(str(GRAY)) == 1958020


def test_mod1051_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1051_times_11000_plus_image_type_times_12900_plus_width_times_1280_plus_height_times_1250
    assert xcf_file_size_mod_1051_times_11000_plus_image_type_times_12900_plus_width_times_1280_plus_height_times_1250(str(RED)) == 1949530


def test_mod1051_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1051_times_11000_plus_image_type_times_12900_plus_width_times_1280_plus_height_times_1250
    assert xcf_file_size_mod_1051_times_11000_plus_image_type_times_12900_plus_width_times_1280_plus_height_times_1250(str(BLUE)) == 1960530


def test_mod1051_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1051_times_11000_plus_image_type_times_12900_plus_width_times_1280_plus_height_times_1250
    assert xcf_file_size_mod_1051_times_11000_plus_image_type_times_12900_plus_width_times_1280_plus_height_times_1250(str(GRAY)) == 1975960


def test_mod1049_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1049_times_10900_plus_image_type_times_12800_plus_width_times_1270_plus_height_times_1240
    assert isinstance(xcf_file_size_mod_1049_times_10900_plus_image_type_times_12800_plus_width_times_1270_plus_height_times_1240(str(RED)), int)


def test_mod1051_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1051_times_11000_plus_image_type_times_12900_plus_width_times_1280_plus_height_times_1250
    assert isinstance(xcf_file_size_mod_1051_times_11000_plus_image_type_times_12900_plus_width_times_1280_plus_height_times_1250(str(RED)), int)


def test_mod1049_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1049_times_10900_plus_image_type_times_12800_plus_width_times_1270_plus_height_times_1240
    assert xcf_file_size_mod_1049_times_10900_plus_image_type_times_12800_plus_width_times_1270_plus_height_times_1240(str(RED)) >= 0


def test_mod1051_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1051_times_11000_plus_image_type_times_12900_plus_width_times_1280_plus_height_times_1250
    assert xcf_file_size_mod_1051_times_11000_plus_image_type_times_12900_plus_width_times_1280_plus_height_times_1250(str(RED)) >= 0


def test_mod1049_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1049_times_10900_plus_image_type_times_12800_plus_width_times_1270_plus_height_times_1240
    fn = xcf_file_size_mod_1049_times_10900_plus_image_type_times_12800_plus_width_times_1270_plus_height_times_1240
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1051_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1051_times_11000_plus_image_type_times_12900_plus_width_times_1280_plus_height_times_1250
    fn = xcf_file_size_mod_1051_times_11000_plus_image_type_times_12900_plus_width_times_1280_plus_height_times_1250
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1049_importable_from_package():
    from xcf import xcf_file_size_mod_1049_times_10900_plus_image_type_times_12800_plus_width_times_1270_plus_height_times_1240
    assert callable(xcf_file_size_mod_1049_times_10900_plus_image_type_times_12800_plus_width_times_1270_plus_height_times_1240)


def test_mod1051_importable_from_package():
    from xcf import xcf_file_size_mod_1051_times_11000_plus_image_type_times_12900_plus_width_times_1280_plus_height_times_1250
    assert callable(xcf_file_size_mod_1051_times_11000_plus_image_type_times_12900_plus_width_times_1280_plus_height_times_1250)
