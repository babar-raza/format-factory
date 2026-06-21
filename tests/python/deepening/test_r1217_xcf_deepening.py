"""Sprint 663 XCF analytics deepening tests - primes 1549, 1553."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1549_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1549_times_17700_plus_image_type_times_19600_plus_width_times_1950_plus_height_times_1920
    assert xcf_file_size_mod_1549_times_17700_plus_image_type_times_19600_plus_width_times_1950_plus_height_times_1920(str(RED)) == 3136770


def test_mod1549_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1549_times_17700_plus_image_type_times_19600_plus_width_times_1950_plus_height_times_1920
    assert xcf_file_size_mod_1549_times_17700_plus_image_type_times_19600_plus_width_times_1950_plus_height_times_1920(str(BLUE)) == 3154470


def test_mod1549_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1549_times_17700_plus_image_type_times_19600_plus_width_times_1950_plus_height_times_1920
    assert xcf_file_size_mod_1549_times_17700_plus_image_type_times_19600_plus_width_times_1950_plus_height_times_1920(str(GRAY)) == 3177940


def test_mod1553_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1553_times_17800_plus_image_type_times_19700_plus_width_times_1960_plus_height_times_1930
    assert xcf_file_size_mod_1553_times_17800_plus_image_type_times_19700_plus_width_times_1960_plus_height_times_1930(str(RED)) == 3154490


def test_mod1553_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1553_times_17800_plus_image_type_times_19700_plus_width_times_1960_plus_height_times_1930
    assert xcf_file_size_mod_1553_times_17800_plus_image_type_times_19700_plus_width_times_1960_plus_height_times_1930(str(BLUE)) == 3172290


def test_mod1553_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1553_times_17800_plus_image_type_times_19700_plus_width_times_1960_plus_height_times_1930
    assert xcf_file_size_mod_1553_times_17800_plus_image_type_times_19700_plus_width_times_1960_plus_height_times_1930(str(GRAY)) == 3195880


def test_mod1549_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1549_times_17700_plus_image_type_times_19600_plus_width_times_1950_plus_height_times_1920
    assert isinstance(xcf_file_size_mod_1549_times_17700_plus_image_type_times_19600_plus_width_times_1950_plus_height_times_1920(str(RED)), int)


def test_mod1553_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1553_times_17800_plus_image_type_times_19700_plus_width_times_1960_plus_height_times_1930
    assert isinstance(xcf_file_size_mod_1553_times_17800_plus_image_type_times_19700_plus_width_times_1960_plus_height_times_1930(str(RED)), int)


def test_mod1549_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1549_times_17700_plus_image_type_times_19600_plus_width_times_1950_plus_height_times_1920
    assert xcf_file_size_mod_1549_times_17700_plus_image_type_times_19600_plus_width_times_1950_plus_height_times_1920(str(RED)) >= 0


def test_mod1553_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1553_times_17800_plus_image_type_times_19700_plus_width_times_1960_plus_height_times_1930
    assert xcf_file_size_mod_1553_times_17800_plus_image_type_times_19700_plus_width_times_1960_plus_height_times_1930(str(RED)) >= 0


def test_mod1549_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1549_times_17700_plus_image_type_times_19600_plus_width_times_1950_plus_height_times_1920
    fn = xcf_file_size_mod_1549_times_17700_plus_image_type_times_19600_plus_width_times_1950_plus_height_times_1920
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1553_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1553_times_17800_plus_image_type_times_19700_plus_width_times_1960_plus_height_times_1930
    fn = xcf_file_size_mod_1553_times_17800_plus_image_type_times_19700_plus_width_times_1960_plus_height_times_1930
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1549_importable_from_package():
    from xcf import xcf_file_size_mod_1549_times_17700_plus_image_type_times_19600_plus_width_times_1950_plus_height_times_1920
    assert callable(xcf_file_size_mod_1549_times_17700_plus_image_type_times_19600_plus_width_times_1950_plus_height_times_1920)


def test_mod1553_importable_from_package():
    from xcf import xcf_file_size_mod_1553_times_17800_plus_image_type_times_19700_plus_width_times_1960_plus_height_times_1930
    assert callable(xcf_file_size_mod_1553_times_17800_plus_image_type_times_19700_plus_width_times_1960_plus_height_times_1930)
