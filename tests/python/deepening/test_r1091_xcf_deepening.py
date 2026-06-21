"""Sprint 537 XCF analytics deepening tests — primes 941, 947."""
import pytest
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod941_red():
    from xcf.xcf_analytics import xcf_file_size_mod_941_times_9300_plus_image_type_times_11200_plus_width_times_1110_plus_height_times_1080
    assert xcf_file_size_mod_941_times_9300_plus_image_type_times_11200_plus_width_times_1110_plus_height_times_1080(str(RED)) == 1648290


def test_mod941_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_941_times_9300_plus_image_type_times_11200_plus_width_times_1110_plus_height_times_1080
    assert xcf_file_size_mod_941_times_9300_plus_image_type_times_11200_plus_width_times_1110_plus_height_times_1080(str(BLUE)) == 1657590


def test_mod941_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_941_times_9300_plus_image_type_times_11200_plus_width_times_1110_plus_height_times_1080
    assert xcf_file_size_mod_941_times_9300_plus_image_type_times_11200_plus_width_times_1110_plus_height_times_1080(str(GRAY)) == 1670980


def test_mod947_red():
    from xcf.xcf_analytics import xcf_file_size_mod_947_times_9400_plus_image_type_times_11300_plus_width_times_1120_plus_height_times_1090
    assert xcf_file_size_mod_947_times_9400_plus_image_type_times_11300_plus_width_times_1120_plus_height_times_1090(str(RED)) == 1666010


def test_mod947_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_947_times_9400_plus_image_type_times_11300_plus_width_times_1120_plus_height_times_1090
    assert xcf_file_size_mod_947_times_9400_plus_image_type_times_11300_plus_width_times_1120_plus_height_times_1090(str(BLUE)) == 1675410


def test_mod947_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_947_times_9400_plus_image_type_times_11300_plus_width_times_1120_plus_height_times_1090
    assert xcf_file_size_mod_947_times_9400_plus_image_type_times_11300_plus_width_times_1120_plus_height_times_1090(str(GRAY)) == 1688920


def test_mod941_returns_int_red():
    from xcf.xcf_analytics import xcf_file_size_mod_941_times_9300_plus_image_type_times_11200_plus_width_times_1110_plus_height_times_1080
    result = xcf_file_size_mod_941_times_9300_plus_image_type_times_11200_plus_width_times_1110_plus_height_times_1080(str(RED))
    assert isinstance(result, int)


def test_mod947_returns_int_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_947_times_9400_plus_image_type_times_11300_plus_width_times_1120_plus_height_times_1090
    result = xcf_file_size_mod_947_times_9400_plus_image_type_times_11300_plus_width_times_1120_plus_height_times_1090(str(BLUE))
    assert isinstance(result, int)


def test_mod941_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_941_times_9300_plus_image_type_times_11200_plus_width_times_1110_plus_height_times_1080
    assert xcf_file_size_mod_941_times_9300_plus_image_type_times_11200_plus_width_times_1110_plus_height_times_1080(str(RED)) >= 0


def test_mod947_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_947_times_9400_plus_image_type_times_11300_plus_width_times_1120_plus_height_times_1090
    assert xcf_file_size_mod_947_times_9400_plus_image_type_times_11300_plus_width_times_1120_plus_height_times_1090(str(RED)) >= 0


def test_mod941_importable_from_package():
    from xcf import xcf_file_size_mod_941_times_9300_plus_image_type_times_11200_plus_width_times_1110_plus_height_times_1080
    assert callable(xcf_file_size_mod_941_times_9300_plus_image_type_times_11200_plus_width_times_1110_plus_height_times_1080)


def test_mod947_importable_from_package():
    from xcf import xcf_file_size_mod_947_times_9400_plus_image_type_times_11300_plus_width_times_1120_plus_height_times_1090
    assert callable(xcf_file_size_mod_947_times_9400_plus_image_type_times_11300_plus_width_times_1120_plus_height_times_1090)


def test_mod941_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_941_times_9300_plus_image_type_times_11200_plus_width_times_1110_plus_height_times_1080
    fn = xcf_file_size_mod_941_times_9300_plus_image_type_times_11200_plus_width_times_1110_plus_height_times_1080
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod947_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_947_times_9400_plus_image_type_times_11300_plus_width_times_1120_plus_height_times_1090
    fn = xcf_file_size_mod_947_times_9400_plus_image_type_times_11300_plus_width_times_1120_plus_height_times_1090
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3
