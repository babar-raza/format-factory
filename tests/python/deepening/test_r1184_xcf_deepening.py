"""Sprint 630 XCF analytics deepening tests - primes 1399, 1409."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1399_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1399_times_15500_plus_image_type_times_17400_plus_width_times_1730_plus_height_times_1700
    assert xcf_file_size_mod_1399_times_15500_plus_image_type_times_17400_plus_width_times_1730_plus_height_times_1700(str(RED)) == 2746930


def test_mod1399_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1399_times_15500_plus_image_type_times_17400_plus_width_times_1730_plus_height_times_1700
    assert xcf_file_size_mod_1399_times_15500_plus_image_type_times_17400_plus_width_times_1730_plus_height_times_1700(str(BLUE)) == 2762430


def test_mod1399_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1399_times_15500_plus_image_type_times_17400_plus_width_times_1730_plus_height_times_1700
    assert xcf_file_size_mod_1399_times_15500_plus_image_type_times_17400_plus_width_times_1730_plus_height_times_1700(str(GRAY)) == 2783260


def test_mod1409_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1409_times_15600_plus_image_type_times_17500_plus_width_times_1740_plus_height_times_1710
    assert xcf_file_size_mod_1409_times_15600_plus_image_type_times_17500_plus_width_times_1740_plus_height_times_1710(str(RED)) == 2764650


def test_mod1409_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1409_times_15600_plus_image_type_times_17500_plus_width_times_1740_plus_height_times_1710
    assert xcf_file_size_mod_1409_times_15600_plus_image_type_times_17500_plus_width_times_1740_plus_height_times_1710(str(BLUE)) == 2780250


def test_mod1409_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1409_times_15600_plus_image_type_times_17500_plus_width_times_1740_plus_height_times_1710
    assert xcf_file_size_mod_1409_times_15600_plus_image_type_times_17500_plus_width_times_1740_plus_height_times_1710(str(GRAY)) == 2801200


def test_mod1399_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1399_times_15500_plus_image_type_times_17400_plus_width_times_1730_plus_height_times_1700
    assert isinstance(xcf_file_size_mod_1399_times_15500_plus_image_type_times_17400_plus_width_times_1730_plus_height_times_1700(str(RED)), int)


def test_mod1409_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1409_times_15600_plus_image_type_times_17500_plus_width_times_1740_plus_height_times_1710
    assert isinstance(xcf_file_size_mod_1409_times_15600_plus_image_type_times_17500_plus_width_times_1740_plus_height_times_1710(str(RED)), int)


def test_mod1399_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1399_times_15500_plus_image_type_times_17400_plus_width_times_1730_plus_height_times_1700
    assert xcf_file_size_mod_1399_times_15500_plus_image_type_times_17400_plus_width_times_1730_plus_height_times_1700(str(RED)) >= 0


def test_mod1409_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1409_times_15600_plus_image_type_times_17500_plus_width_times_1740_plus_height_times_1710
    assert xcf_file_size_mod_1409_times_15600_plus_image_type_times_17500_plus_width_times_1740_plus_height_times_1710(str(RED)) >= 0


def test_mod1399_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1399_times_15500_plus_image_type_times_17400_plus_width_times_1730_plus_height_times_1700
    fn = xcf_file_size_mod_1399_times_15500_plus_image_type_times_17400_plus_width_times_1730_plus_height_times_1700
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1409_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1409_times_15600_plus_image_type_times_17500_plus_width_times_1740_plus_height_times_1710
    fn = xcf_file_size_mod_1409_times_15600_plus_image_type_times_17500_plus_width_times_1740_plus_height_times_1710
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1399_importable_from_package():
    from xcf import xcf_file_size_mod_1399_times_15500_plus_image_type_times_17400_plus_width_times_1730_plus_height_times_1700
    assert callable(xcf_file_size_mod_1399_times_15500_plus_image_type_times_17400_plus_width_times_1730_plus_height_times_1700)


def test_mod1409_importable_from_package():
    from xcf import xcf_file_size_mod_1409_times_15600_plus_image_type_times_17500_plus_width_times_1740_plus_height_times_1710
    assert callable(xcf_file_size_mod_1409_times_15600_plus_image_type_times_17500_plus_width_times_1740_plus_height_times_1710)
