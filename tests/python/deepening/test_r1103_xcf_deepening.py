"""Sprint 549 XCF analytics deepening tests - primes 997, 1009."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod997_red():
    from xcf.xcf_analytics import xcf_file_size_mod_997_times_10100_plus_image_type_times_12000_plus_width_times_1190_plus_height_times_1160
    assert xcf_file_size_mod_997_times_10100_plus_image_type_times_12000_plus_width_times_1190_plus_height_times_1160(str(RED)) == 1790050


def test_mod997_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_997_times_10100_plus_image_type_times_12000_plus_width_times_1190_plus_height_times_1160
    assert xcf_file_size_mod_997_times_10100_plus_image_type_times_12000_plus_width_times_1190_plus_height_times_1160(str(BLUE)) == 1800150


def test_mod997_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_997_times_10100_plus_image_type_times_12000_plus_width_times_1190_plus_height_times_1160
    assert xcf_file_size_mod_997_times_10100_plus_image_type_times_12000_plus_width_times_1190_plus_height_times_1160(str(GRAY)) == 1814500


def test_mod1009_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1009_times_10200_plus_image_type_times_12100_plus_width_times_1200_plus_height_times_1170
    assert xcf_file_size_mod_1009_times_10200_plus_image_type_times_12100_plus_width_times_1200_plus_height_times_1170(str(RED)) == 1807770


def test_mod1009_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1009_times_10200_plus_image_type_times_12100_plus_width_times_1200_plus_height_times_1170
    assert xcf_file_size_mod_1009_times_10200_plus_image_type_times_12100_plus_width_times_1200_plus_height_times_1170(str(BLUE)) == 1817970


def test_mod1009_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1009_times_10200_plus_image_type_times_12100_plus_width_times_1200_plus_height_times_1170
    assert xcf_file_size_mod_1009_times_10200_plus_image_type_times_12100_plus_width_times_1200_plus_height_times_1170(str(GRAY)) == 1832440


def test_mod997_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_997_times_10100_plus_image_type_times_12000_plus_width_times_1190_plus_height_times_1160
    assert isinstance(xcf_file_size_mod_997_times_10100_plus_image_type_times_12000_plus_width_times_1190_plus_height_times_1160(str(RED)), int)


def test_mod1009_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1009_times_10200_plus_image_type_times_12100_plus_width_times_1200_plus_height_times_1170
    assert isinstance(xcf_file_size_mod_1009_times_10200_plus_image_type_times_12100_plus_width_times_1200_plus_height_times_1170(str(RED)), int)


def test_mod997_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_997_times_10100_plus_image_type_times_12000_plus_width_times_1190_plus_height_times_1160
    assert xcf_file_size_mod_997_times_10100_plus_image_type_times_12000_plus_width_times_1190_plus_height_times_1160(str(RED)) >= 0


def test_mod1009_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1009_times_10200_plus_image_type_times_12100_plus_width_times_1200_plus_height_times_1170
    assert xcf_file_size_mod_1009_times_10200_plus_image_type_times_12100_plus_width_times_1200_plus_height_times_1170(str(RED)) >= 0


def test_mod997_importable_from_package():
    from xcf import xcf_file_size_mod_997_times_10100_plus_image_type_times_12000_plus_width_times_1190_plus_height_times_1160
    assert callable(xcf_file_size_mod_997_times_10100_plus_image_type_times_12000_plus_width_times_1190_plus_height_times_1160)


def test_mod1009_importable_from_package():
    from xcf import xcf_file_size_mod_1009_times_10200_plus_image_type_times_12100_plus_width_times_1200_plus_height_times_1170
    assert callable(xcf_file_size_mod_1009_times_10200_plus_image_type_times_12100_plus_width_times_1200_plus_height_times_1170)


def test_mod997_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_997_times_10100_plus_image_type_times_12000_plus_width_times_1190_plus_height_times_1160
    fn = xcf_file_size_mod_997_times_10100_plus_image_type_times_12000_plus_width_times_1190_plus_height_times_1160
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1009_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1009_times_10200_plus_image_type_times_12100_plus_width_times_1200_plus_height_times_1170
    fn = xcf_file_size_mod_1009_times_10200_plus_image_type_times_12100_plus_width_times_1200_plus_height_times_1170
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3
