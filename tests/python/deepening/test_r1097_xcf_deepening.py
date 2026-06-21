"""Sprint 543 XCF analytics deepening tests — primes 971, 977."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod971_red():
    from xcf.xcf_analytics import xcf_file_size_mod_971_times_9700_plus_image_type_times_11600_plus_width_times_1150_plus_height_times_1120
    assert xcf_file_size_mod_971_times_9700_plus_image_type_times_11600_plus_width_times_1150_plus_height_times_1120(str(RED)) == 1719170


def test_mod971_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_971_times_9700_plus_image_type_times_11600_plus_width_times_1150_plus_height_times_1120
    assert xcf_file_size_mod_971_times_9700_plus_image_type_times_11600_plus_width_times_1150_plus_height_times_1120(str(BLUE)) == 1728870


def test_mod971_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_971_times_9700_plus_image_type_times_11600_plus_width_times_1150_plus_height_times_1120
    assert xcf_file_size_mod_971_times_9700_plus_image_type_times_11600_plus_width_times_1150_plus_height_times_1120(str(GRAY)) == 1742740


def test_mod977_red():
    from xcf.xcf_analytics import xcf_file_size_mod_977_times_9800_plus_image_type_times_11700_plus_width_times_1160_plus_height_times_1130
    assert xcf_file_size_mod_977_times_9800_plus_image_type_times_11700_plus_width_times_1160_plus_height_times_1130(str(RED)) == 1736890


def test_mod977_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_977_times_9800_plus_image_type_times_11700_plus_width_times_1160_plus_height_times_1130
    assert xcf_file_size_mod_977_times_9800_plus_image_type_times_11700_plus_width_times_1160_plus_height_times_1130(str(BLUE)) == 1746690


def test_mod977_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_977_times_9800_plus_image_type_times_11700_plus_width_times_1160_plus_height_times_1130
    assert xcf_file_size_mod_977_times_9800_plus_image_type_times_11700_plus_width_times_1160_plus_height_times_1130(str(GRAY)) == 1760680


def test_mod971_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_971_times_9700_plus_image_type_times_11600_plus_width_times_1150_plus_height_times_1120
    assert isinstance(xcf_file_size_mod_971_times_9700_plus_image_type_times_11600_plus_width_times_1150_plus_height_times_1120(str(RED)), int)


def test_mod977_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_977_times_9800_plus_image_type_times_11700_plus_width_times_1160_plus_height_times_1130
    assert isinstance(xcf_file_size_mod_977_times_9800_plus_image_type_times_11700_plus_width_times_1160_plus_height_times_1130(str(RED)), int)


def test_mod971_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_971_times_9700_plus_image_type_times_11600_plus_width_times_1150_plus_height_times_1120
    assert xcf_file_size_mod_971_times_9700_plus_image_type_times_11600_plus_width_times_1150_plus_height_times_1120(str(RED)) >= 0


def test_mod977_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_977_times_9800_plus_image_type_times_11700_plus_width_times_1160_plus_height_times_1130
    assert xcf_file_size_mod_977_times_9800_plus_image_type_times_11700_plus_width_times_1160_plus_height_times_1130(str(RED)) >= 0


def test_mod971_importable_from_package():
    from xcf import xcf_file_size_mod_971_times_9700_plus_image_type_times_11600_plus_width_times_1150_plus_height_times_1120
    assert callable(xcf_file_size_mod_971_times_9700_plus_image_type_times_11600_plus_width_times_1150_plus_height_times_1120)


def test_mod977_importable_from_package():
    from xcf import xcf_file_size_mod_977_times_9800_plus_image_type_times_11700_plus_width_times_1160_plus_height_times_1130
    assert callable(xcf_file_size_mod_977_times_9800_plus_image_type_times_11700_plus_width_times_1160_plus_height_times_1130)


def test_mod971_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_971_times_9700_plus_image_type_times_11600_plus_width_times_1150_plus_height_times_1120
    fn = xcf_file_size_mod_971_times_9700_plus_image_type_times_11600_plus_width_times_1150_plus_height_times_1120
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod977_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_977_times_9800_plus_image_type_times_11700_plus_width_times_1160_plus_height_times_1130
    fn = xcf_file_size_mod_977_times_9800_plus_image_type_times_11700_plus_width_times_1160_plus_height_times_1130
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3
