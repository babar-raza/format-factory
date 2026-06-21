"""Sprint 540 XCF analytics deepening tests — primes 953, 967."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod953_red():
    from xcf.xcf_analytics import xcf_file_size_mod_953_times_9500_plus_image_type_times_11400_plus_width_times_1130_plus_height_times_1100
    assert xcf_file_size_mod_953_times_9500_plus_image_type_times_11400_plus_width_times_1130_plus_height_times_1100(str(RED)) == 1683730


def test_mod953_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_953_times_9500_plus_image_type_times_11400_plus_width_times_1130_plus_height_times_1100
    assert xcf_file_size_mod_953_times_9500_plus_image_type_times_11400_plus_width_times_1130_plus_height_times_1100(str(BLUE)) == 1693230


def test_mod953_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_953_times_9500_plus_image_type_times_11400_plus_width_times_1130_plus_height_times_1100
    assert xcf_file_size_mod_953_times_9500_plus_image_type_times_11400_plus_width_times_1130_plus_height_times_1100(str(GRAY)) == 1706860


def test_mod967_red():
    from xcf.xcf_analytics import xcf_file_size_mod_967_times_9600_plus_image_type_times_11500_plus_width_times_1140_plus_height_times_1110
    assert xcf_file_size_mod_967_times_9600_plus_image_type_times_11500_plus_width_times_1140_plus_height_times_1110(str(RED)) == 1701450


def test_mod967_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_967_times_9600_plus_image_type_times_11500_plus_width_times_1140_plus_height_times_1110
    assert xcf_file_size_mod_967_times_9600_plus_image_type_times_11500_plus_width_times_1140_plus_height_times_1110(str(BLUE)) == 1711050


def test_mod967_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_967_times_9600_plus_image_type_times_11500_plus_width_times_1140_plus_height_times_1110
    assert xcf_file_size_mod_967_times_9600_plus_image_type_times_11500_plus_width_times_1140_plus_height_times_1110(str(GRAY)) == 1724800


def test_mod953_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_953_times_9500_plus_image_type_times_11400_plus_width_times_1130_plus_height_times_1100
    assert isinstance(xcf_file_size_mod_953_times_9500_plus_image_type_times_11400_plus_width_times_1130_plus_height_times_1100(str(RED)), int)


def test_mod967_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_967_times_9600_plus_image_type_times_11500_plus_width_times_1140_plus_height_times_1110
    assert isinstance(xcf_file_size_mod_967_times_9600_plus_image_type_times_11500_plus_width_times_1140_plus_height_times_1110(str(RED)), int)


def test_mod953_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_953_times_9500_plus_image_type_times_11400_plus_width_times_1130_plus_height_times_1100
    assert xcf_file_size_mod_953_times_9500_plus_image_type_times_11400_plus_width_times_1130_plus_height_times_1100(str(RED)) >= 0


def test_mod967_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_967_times_9600_plus_image_type_times_11500_plus_width_times_1140_plus_height_times_1110
    assert xcf_file_size_mod_967_times_9600_plus_image_type_times_11500_plus_width_times_1140_plus_height_times_1110(str(RED)) >= 0


def test_mod953_importable_from_package():
    from xcf import xcf_file_size_mod_953_times_9500_plus_image_type_times_11400_plus_width_times_1130_plus_height_times_1100
    assert callable(xcf_file_size_mod_953_times_9500_plus_image_type_times_11400_plus_width_times_1130_plus_height_times_1100)


def test_mod967_importable_from_package():
    from xcf import xcf_file_size_mod_967_times_9600_plus_image_type_times_11500_plus_width_times_1140_plus_height_times_1110
    assert callable(xcf_file_size_mod_967_times_9600_plus_image_type_times_11500_plus_width_times_1140_plus_height_times_1110)


def test_mod953_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_953_times_9500_plus_image_type_times_11400_plus_width_times_1130_plus_height_times_1100
    fn = xcf_file_size_mod_953_times_9500_plus_image_type_times_11400_plus_width_times_1130_plus_height_times_1100
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod967_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_967_times_9600_plus_image_type_times_11500_plus_width_times_1140_plus_height_times_1110
    fn = xcf_file_size_mod_967_times_9600_plus_image_type_times_11500_plus_width_times_1140_plus_height_times_1110
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3
