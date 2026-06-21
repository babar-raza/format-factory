"""Sprint 657 XCF analytics deepening tests - primes 1511, 1523."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1511_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1511_times_17300_plus_image_type_times_19200_plus_width_times_1910_plus_height_times_1880
    assert xcf_file_size_mod_1511_times_17300_plus_image_type_times_19200_plus_width_times_1910_plus_height_times_1880(str(RED)) == 3065890


def test_mod1511_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1511_times_17300_plus_image_type_times_19200_plus_width_times_1910_plus_height_times_1880
    assert xcf_file_size_mod_1511_times_17300_plus_image_type_times_19200_plus_width_times_1910_plus_height_times_1880(str(BLUE)) == 3083190


def test_mod1511_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1511_times_17300_plus_image_type_times_19200_plus_width_times_1910_plus_height_times_1880
    assert xcf_file_size_mod_1511_times_17300_plus_image_type_times_19200_plus_width_times_1910_plus_height_times_1880(str(GRAY)) == 3106180


def test_mod1523_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1523_times_17400_plus_image_type_times_19300_plus_width_times_1920_plus_height_times_1890
    assert xcf_file_size_mod_1523_times_17400_plus_image_type_times_19300_plus_width_times_1920_plus_height_times_1890(str(RED)) == 3083610


def test_mod1523_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1523_times_17400_plus_image_type_times_19300_plus_width_times_1920_plus_height_times_1890
    assert xcf_file_size_mod_1523_times_17400_plus_image_type_times_19300_plus_width_times_1920_plus_height_times_1890(str(BLUE)) == 3101010


def test_mod1523_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1523_times_17400_plus_image_type_times_19300_plus_width_times_1920_plus_height_times_1890
    assert xcf_file_size_mod_1523_times_17400_plus_image_type_times_19300_plus_width_times_1920_plus_height_times_1890(str(GRAY)) == 3124120


def test_mod1511_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1511_times_17300_plus_image_type_times_19200_plus_width_times_1910_plus_height_times_1880
    assert isinstance(xcf_file_size_mod_1511_times_17300_plus_image_type_times_19200_plus_width_times_1910_plus_height_times_1880(str(RED)), int)


def test_mod1523_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1523_times_17400_plus_image_type_times_19300_plus_width_times_1920_plus_height_times_1890
    assert isinstance(xcf_file_size_mod_1523_times_17400_plus_image_type_times_19300_plus_width_times_1920_plus_height_times_1890(str(RED)), int)


def test_mod1511_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1511_times_17300_plus_image_type_times_19200_plus_width_times_1910_plus_height_times_1880
    assert xcf_file_size_mod_1511_times_17300_plus_image_type_times_19200_plus_width_times_1910_plus_height_times_1880(str(RED)) >= 0


def test_mod1523_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1523_times_17400_plus_image_type_times_19300_plus_width_times_1920_plus_height_times_1890
    assert xcf_file_size_mod_1523_times_17400_plus_image_type_times_19300_plus_width_times_1920_plus_height_times_1890(str(RED)) >= 0


def test_mod1511_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1511_times_17300_plus_image_type_times_19200_plus_width_times_1910_plus_height_times_1880
    fn = xcf_file_size_mod_1511_times_17300_plus_image_type_times_19200_plus_width_times_1910_plus_height_times_1880
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1523_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1523_times_17400_plus_image_type_times_19300_plus_width_times_1920_plus_height_times_1890
    fn = xcf_file_size_mod_1523_times_17400_plus_image_type_times_19300_plus_width_times_1920_plus_height_times_1890
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1511_importable_from_package():
    from xcf import xcf_file_size_mod_1511_times_17300_plus_image_type_times_19200_plus_width_times_1910_plus_height_times_1880
    assert callable(xcf_file_size_mod_1511_times_17300_plus_image_type_times_19200_plus_width_times_1910_plus_height_times_1880)


def test_mod1523_importable_from_package():
    from xcf import xcf_file_size_mod_1523_times_17400_plus_image_type_times_19300_plus_width_times_1920_plus_height_times_1890
    assert callable(xcf_file_size_mod_1523_times_17400_plus_image_type_times_19300_plus_width_times_1920_plus_height_times_1890)
