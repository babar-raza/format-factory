"""Sprint 555 XCF analytics deepening tests - primes 1021, 1031."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1021_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1021_times_10500_plus_image_type_times_12400_plus_width_times_1230_plus_height_times_1200
    assert xcf_file_size_mod_1021_times_10500_plus_image_type_times_12400_plus_width_times_1230_plus_height_times_1200(str(RED)) == 1860930


def test_mod1021_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1021_times_10500_plus_image_type_times_12400_plus_width_times_1230_plus_height_times_1200
    assert xcf_file_size_mod_1021_times_10500_plus_image_type_times_12400_plus_width_times_1230_plus_height_times_1200(str(BLUE)) == 1871430


def test_mod1021_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1021_times_10500_plus_image_type_times_12400_plus_width_times_1230_plus_height_times_1200
    assert xcf_file_size_mod_1021_times_10500_plus_image_type_times_12400_plus_width_times_1230_plus_height_times_1200(str(GRAY)) == 1886260


def test_mod1031_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1031_times_10600_plus_image_type_times_12500_plus_width_times_1240_plus_height_times_1210
    assert xcf_file_size_mod_1031_times_10600_plus_image_type_times_12500_plus_width_times_1240_plus_height_times_1210(str(RED)) == 1878650


def test_mod1031_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1031_times_10600_plus_image_type_times_12500_plus_width_times_1240_plus_height_times_1210
    assert xcf_file_size_mod_1031_times_10600_plus_image_type_times_12500_plus_width_times_1240_plus_height_times_1210(str(BLUE)) == 1889250


def test_mod1031_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1031_times_10600_plus_image_type_times_12500_plus_width_times_1240_plus_height_times_1210
    assert xcf_file_size_mod_1031_times_10600_plus_image_type_times_12500_plus_width_times_1240_plus_height_times_1210(str(GRAY)) == 1904200


def test_mod1021_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1021_times_10500_plus_image_type_times_12400_plus_width_times_1230_plus_height_times_1200
    assert isinstance(xcf_file_size_mod_1021_times_10500_plus_image_type_times_12400_plus_width_times_1230_plus_height_times_1200(str(RED)), int)


def test_mod1031_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1031_times_10600_plus_image_type_times_12500_plus_width_times_1240_plus_height_times_1210
    assert isinstance(xcf_file_size_mod_1031_times_10600_plus_image_type_times_12500_plus_width_times_1240_plus_height_times_1210(str(RED)), int)


def test_mod1021_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1021_times_10500_plus_image_type_times_12400_plus_width_times_1230_plus_height_times_1200
    assert xcf_file_size_mod_1021_times_10500_plus_image_type_times_12400_plus_width_times_1230_plus_height_times_1200(str(RED)) >= 0


def test_mod1031_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1031_times_10600_plus_image_type_times_12500_plus_width_times_1240_plus_height_times_1210
    assert xcf_file_size_mod_1031_times_10600_plus_image_type_times_12500_plus_width_times_1240_plus_height_times_1210(str(RED)) >= 0


def test_mod1021_importable_from_package():
    from xcf import xcf_file_size_mod_1021_times_10500_plus_image_type_times_12400_plus_width_times_1230_plus_height_times_1200
    assert callable(xcf_file_size_mod_1021_times_10500_plus_image_type_times_12400_plus_width_times_1230_plus_height_times_1200)


def test_mod1031_importable_from_package():
    from xcf import xcf_file_size_mod_1031_times_10600_plus_image_type_times_12500_plus_width_times_1240_plus_height_times_1210
    assert callable(xcf_file_size_mod_1031_times_10600_plus_image_type_times_12500_plus_width_times_1240_plus_height_times_1210)


def test_mod1021_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1021_times_10500_plus_image_type_times_12400_plus_width_times_1230_plus_height_times_1200
    fn = xcf_file_size_mod_1021_times_10500_plus_image_type_times_12400_plus_width_times_1230_plus_height_times_1200
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1031_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1031_times_10600_plus_image_type_times_12500_plus_width_times_1240_plus_height_times_1210
    fn = xcf_file_size_mod_1031_times_10600_plus_image_type_times_12500_plus_width_times_1240_plus_height_times_1210
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3
