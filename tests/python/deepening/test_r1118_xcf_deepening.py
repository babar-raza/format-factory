"""Sprint 564 XCF analytics deepening tests - primes 1061, 1063."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1061_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1061_times_11100_plus_image_type_times_13000_plus_width_times_1290_plus_height_times_1260
    assert xcf_file_size_mod_1061_times_11100_plus_image_type_times_13000_plus_width_times_1290_plus_height_times_1260(str(RED)) == 1967250


def test_mod1061_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1061_times_11100_plus_image_type_times_13000_plus_width_times_1290_plus_height_times_1260
    assert xcf_file_size_mod_1061_times_11100_plus_image_type_times_13000_plus_width_times_1290_plus_height_times_1260(str(BLUE)) == 1978350


def test_mod1061_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1061_times_11100_plus_image_type_times_13000_plus_width_times_1290_plus_height_times_1260
    assert xcf_file_size_mod_1061_times_11100_plus_image_type_times_13000_plus_width_times_1290_plus_height_times_1260(str(GRAY)) == 1993900


def test_mod1063_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1063_times_11200_plus_image_type_times_13100_plus_width_times_1300_plus_height_times_1270
    assert xcf_file_size_mod_1063_times_11200_plus_image_type_times_13100_plus_width_times_1300_plus_height_times_1270(str(RED)) == 1984970


def test_mod1063_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1063_times_11200_plus_image_type_times_13100_plus_width_times_1300_plus_height_times_1270
    assert xcf_file_size_mod_1063_times_11200_plus_image_type_times_13100_plus_width_times_1300_plus_height_times_1270(str(BLUE)) == 1996170


def test_mod1063_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1063_times_11200_plus_image_type_times_13100_plus_width_times_1300_plus_height_times_1270
    assert xcf_file_size_mod_1063_times_11200_plus_image_type_times_13100_plus_width_times_1300_plus_height_times_1270(str(GRAY)) == 2011840


def test_mod1061_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1061_times_11100_plus_image_type_times_13000_plus_width_times_1290_plus_height_times_1260
    assert isinstance(xcf_file_size_mod_1061_times_11100_plus_image_type_times_13000_plus_width_times_1290_plus_height_times_1260(str(RED)), int)


def test_mod1063_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1063_times_11200_plus_image_type_times_13100_plus_width_times_1300_plus_height_times_1270
    assert isinstance(xcf_file_size_mod_1063_times_11200_plus_image_type_times_13100_plus_width_times_1300_plus_height_times_1270(str(RED)), int)


def test_mod1061_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1061_times_11100_plus_image_type_times_13000_plus_width_times_1290_plus_height_times_1260
    assert xcf_file_size_mod_1061_times_11100_plus_image_type_times_13000_plus_width_times_1290_plus_height_times_1260(str(RED)) >= 0


def test_mod1063_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1063_times_11200_plus_image_type_times_13100_plus_width_times_1300_plus_height_times_1270
    assert xcf_file_size_mod_1063_times_11200_plus_image_type_times_13100_plus_width_times_1300_plus_height_times_1270(str(RED)) >= 0


def test_mod1061_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1061_times_11100_plus_image_type_times_13000_plus_width_times_1290_plus_height_times_1260
    fn = xcf_file_size_mod_1061_times_11100_plus_image_type_times_13000_plus_width_times_1290_plus_height_times_1260
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1063_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1063_times_11200_plus_image_type_times_13100_plus_width_times_1300_plus_height_times_1270
    fn = xcf_file_size_mod_1063_times_11200_plus_image_type_times_13100_plus_width_times_1300_plus_height_times_1270
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1061_importable_from_package():
    from xcf import xcf_file_size_mod_1061_times_11100_plus_image_type_times_13000_plus_width_times_1290_plus_height_times_1260
    assert callable(xcf_file_size_mod_1061_times_11100_plus_image_type_times_13000_plus_width_times_1290_plus_height_times_1260)


def test_mod1063_importable_from_package():
    from xcf import xcf_file_size_mod_1063_times_11200_plus_image_type_times_13100_plus_width_times_1300_plus_height_times_1270
    assert callable(xcf_file_size_mod_1063_times_11200_plus_image_type_times_13100_plus_width_times_1300_plus_height_times_1270)
