"""Sprint 567 XCF analytics deepening tests - primes 1069, 1087."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1069_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1069_times_11300_plus_image_type_times_13200_plus_width_times_1310_plus_height_times_1280
    assert xcf_file_size_mod_1069_times_11300_plus_image_type_times_13200_plus_width_times_1310_plus_height_times_1280(str(RED)) == 2002690


def test_mod1069_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1069_times_11300_plus_image_type_times_13200_plus_width_times_1310_plus_height_times_1280
    assert xcf_file_size_mod_1069_times_11300_plus_image_type_times_13200_plus_width_times_1310_plus_height_times_1280(str(BLUE)) == 2013990


def test_mod1069_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1069_times_11300_plus_image_type_times_13200_plus_width_times_1310_plus_height_times_1280
    assert xcf_file_size_mod_1069_times_11300_plus_image_type_times_13200_plus_width_times_1310_plus_height_times_1280(str(GRAY)) == 2029780


def test_mod1087_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1087_times_11400_plus_image_type_times_13300_plus_width_times_1320_plus_height_times_1290
    assert xcf_file_size_mod_1087_times_11400_plus_image_type_times_13300_plus_width_times_1320_plus_height_times_1290(str(RED)) == 2020410


def test_mod1087_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1087_times_11400_plus_image_type_times_13300_plus_width_times_1320_plus_height_times_1290
    assert xcf_file_size_mod_1087_times_11400_plus_image_type_times_13300_plus_width_times_1320_plus_height_times_1290(str(BLUE)) == 2031810


def test_mod1087_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1087_times_11400_plus_image_type_times_13300_plus_width_times_1320_plus_height_times_1290
    assert xcf_file_size_mod_1087_times_11400_plus_image_type_times_13300_plus_width_times_1320_plus_height_times_1290(str(GRAY)) == 2047720


def test_mod1069_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1069_times_11300_plus_image_type_times_13200_plus_width_times_1310_plus_height_times_1280
    assert isinstance(xcf_file_size_mod_1069_times_11300_plus_image_type_times_13200_plus_width_times_1310_plus_height_times_1280(str(RED)), int)


def test_mod1087_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1087_times_11400_plus_image_type_times_13300_plus_width_times_1320_plus_height_times_1290
    assert isinstance(xcf_file_size_mod_1087_times_11400_plus_image_type_times_13300_plus_width_times_1320_plus_height_times_1290(str(RED)), int)


def test_mod1069_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1069_times_11300_plus_image_type_times_13200_plus_width_times_1310_plus_height_times_1280
    assert xcf_file_size_mod_1069_times_11300_plus_image_type_times_13200_plus_width_times_1310_plus_height_times_1280(str(RED)) >= 0


def test_mod1087_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1087_times_11400_plus_image_type_times_13300_plus_width_times_1320_plus_height_times_1290
    assert xcf_file_size_mod_1087_times_11400_plus_image_type_times_13300_plus_width_times_1320_plus_height_times_1290(str(RED)) >= 0


def test_mod1069_importable_from_package():
    from xcf import xcf_file_size_mod_1069_times_11300_plus_image_type_times_13200_plus_width_times_1310_plus_height_times_1280
    assert callable(xcf_file_size_mod_1069_times_11300_plus_image_type_times_13200_plus_width_times_1310_plus_height_times_1280)


def test_mod1087_importable_from_package():
    from xcf import xcf_file_size_mod_1087_times_11400_plus_image_type_times_13300_plus_width_times_1320_plus_height_times_1290
    assert callable(xcf_file_size_mod_1087_times_11400_plus_image_type_times_13300_plus_width_times_1320_plus_height_times_1290)


def test_mod1069_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1069_times_11300_plus_image_type_times_13200_plus_width_times_1310_plus_height_times_1280
    fn = xcf_file_size_mod_1069_times_11300_plus_image_type_times_13200_plus_width_times_1310_plus_height_times_1280
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1087_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1087_times_11400_plus_image_type_times_13300_plus_width_times_1320_plus_height_times_1290
    fn = xcf_file_size_mod_1087_times_11400_plus_image_type_times_13300_plus_width_times_1320_plus_height_times_1290
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3
