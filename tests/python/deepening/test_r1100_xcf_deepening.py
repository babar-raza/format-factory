"""Sprint analytics deepening tests - primes 983, 991."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod983_red():
    from xcf.xcf_analytics import xcf_file_size_mod_983_times_9900_plus_image_type_times_11800_plus_width_times_1170_plus_height_times_1140
    assert xcf_file_size_mod_983_times_9900_plus_image_type_times_11800_plus_width_times_1170_plus_height_times_1140(str(RED)) == 1754610


def test_mod983_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_983_times_9900_plus_image_type_times_11800_plus_width_times_1170_plus_height_times_1140
    assert xcf_file_size_mod_983_times_9900_plus_image_type_times_11800_plus_width_times_1170_plus_height_times_1140(str(BLUE)) == 1764510


def test_mod983_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_983_times_9900_plus_image_type_times_11800_plus_width_times_1170_plus_height_times_1140
    assert xcf_file_size_mod_983_times_9900_plus_image_type_times_11800_plus_width_times_1170_plus_height_times_1140(str(GRAY)) == 1778620


def test_mod991_red():
    from xcf.xcf_analytics import xcf_file_size_mod_991_times_10000_plus_image_type_times_11900_plus_width_times_1180_plus_height_times_1150
    assert xcf_file_size_mod_991_times_10000_plus_image_type_times_11900_plus_width_times_1180_plus_height_times_1150(str(RED)) == 1772330


def test_mod991_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_991_times_10000_plus_image_type_times_11900_plus_width_times_1180_plus_height_times_1150
    assert xcf_file_size_mod_991_times_10000_plus_image_type_times_11900_plus_width_times_1180_plus_height_times_1150(str(BLUE)) == 1782330


def test_mod991_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_991_times_10000_plus_image_type_times_11900_plus_width_times_1180_plus_height_times_1150
    assert xcf_file_size_mod_991_times_10000_plus_image_type_times_11900_plus_width_times_1180_plus_height_times_1150(str(GRAY)) == 1796560


def test_mod983_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_983_times_9900_plus_image_type_times_11800_plus_width_times_1170_plus_height_times_1140
    result = xcf_file_size_mod_983_times_9900_plus_image_type_times_11800_plus_width_times_1170_plus_height_times_1140(str(RED))
    assert isinstance(result, int)


def test_mod991_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_991_times_10000_plus_image_type_times_11900_plus_width_times_1180_plus_height_times_1150
    result = xcf_file_size_mod_991_times_10000_plus_image_type_times_11900_plus_width_times_1180_plus_height_times_1150(str(RED))
    assert isinstance(result, int)


def test_mod983_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_983_times_9900_plus_image_type_times_11800_plus_width_times_1170_plus_height_times_1140
    assert xcf_file_size_mod_983_times_9900_plus_image_type_times_11800_plus_width_times_1170_plus_height_times_1140(str(RED)) >= 0


def test_mod991_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_991_times_10000_plus_image_type_times_11900_plus_width_times_1180_plus_height_times_1150
    assert xcf_file_size_mod_991_times_10000_plus_image_type_times_11900_plus_width_times_1180_plus_height_times_1150(str(RED)) >= 0


def test_mod983_importable_from_package():
    from xcf import xcf_file_size_mod_983_times_9900_plus_image_type_times_11800_plus_width_times_1170_plus_height_times_1140
    assert callable(xcf_file_size_mod_983_times_9900_plus_image_type_times_11800_plus_width_times_1170_plus_height_times_1140)


def test_mod991_importable_from_package():
    from xcf import xcf_file_size_mod_991_times_10000_plus_image_type_times_11900_plus_width_times_1180_plus_height_times_1150
    assert callable(xcf_file_size_mod_991_times_10000_plus_image_type_times_11900_plus_width_times_1180_plus_height_times_1150)


def test_mod983_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_983_times_9900_plus_image_type_times_11800_plus_width_times_1170_plus_height_times_1140
    fn = xcf_file_size_mod_983_times_9900_plus_image_type_times_11800_plus_width_times_1170_plus_height_times_1140
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod991_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_991_times_10000_plus_image_type_times_11900_plus_width_times_1180_plus_height_times_1150
    fn = xcf_file_size_mod_991_times_10000_plus_image_type_times_11900_plus_width_times_1180_plus_height_times_1150
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3
