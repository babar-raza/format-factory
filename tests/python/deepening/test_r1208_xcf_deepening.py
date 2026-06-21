"""Sprint 654 XCF analytics deepening tests - primes 1493, 1499."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1493_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1493_times_17100_plus_image_type_times_19000_plus_width_times_1890_plus_height_times_1860
    assert xcf_file_size_mod_1493_times_17100_plus_image_type_times_19000_plus_width_times_1890_plus_height_times_1860(str(RED)) == 3030450


def test_mod1493_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1493_times_17100_plus_image_type_times_19000_plus_width_times_1890_plus_height_times_1860
    assert xcf_file_size_mod_1493_times_17100_plus_image_type_times_19000_plus_width_times_1890_plus_height_times_1860(str(BLUE)) == 3047550


def test_mod1493_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1493_times_17100_plus_image_type_times_19000_plus_width_times_1890_plus_height_times_1860
    assert xcf_file_size_mod_1493_times_17100_plus_image_type_times_19000_plus_width_times_1890_plus_height_times_1860(str(GRAY)) == 3070300


def test_mod1499_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1499_times_17200_plus_image_type_times_19100_plus_width_times_1900_plus_height_times_1870
    assert xcf_file_size_mod_1499_times_17200_plus_image_type_times_19100_plus_width_times_1900_plus_height_times_1870(str(RED)) == 3048170


def test_mod1499_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1499_times_17200_plus_image_type_times_19100_plus_width_times_1900_plus_height_times_1870
    assert xcf_file_size_mod_1499_times_17200_plus_image_type_times_19100_plus_width_times_1900_plus_height_times_1870(str(BLUE)) == 3065370


def test_mod1499_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1499_times_17200_plus_image_type_times_19100_plus_width_times_1900_plus_height_times_1870
    assert xcf_file_size_mod_1499_times_17200_plus_image_type_times_19100_plus_width_times_1900_plus_height_times_1870(str(GRAY)) == 3088240


def test_mod1493_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1493_times_17100_plus_image_type_times_19000_plus_width_times_1890_plus_height_times_1860
    assert isinstance(xcf_file_size_mod_1493_times_17100_plus_image_type_times_19000_plus_width_times_1890_plus_height_times_1860(str(RED)), int)


def test_mod1499_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1499_times_17200_plus_image_type_times_19100_plus_width_times_1900_plus_height_times_1870
    assert isinstance(xcf_file_size_mod_1499_times_17200_plus_image_type_times_19100_plus_width_times_1900_plus_height_times_1870(str(RED)), int)


def test_mod1493_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1493_times_17100_plus_image_type_times_19000_plus_width_times_1890_plus_height_times_1860
    assert xcf_file_size_mod_1493_times_17100_plus_image_type_times_19000_plus_width_times_1890_plus_height_times_1860(str(RED)) >= 0


def test_mod1499_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1499_times_17200_plus_image_type_times_19100_plus_width_times_1900_plus_height_times_1870
    assert xcf_file_size_mod_1499_times_17200_plus_image_type_times_19100_plus_width_times_1900_plus_height_times_1870(str(RED)) >= 0


def test_mod1493_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1493_times_17100_plus_image_type_times_19000_plus_width_times_1890_plus_height_times_1860
    fn = xcf_file_size_mod_1493_times_17100_plus_image_type_times_19000_plus_width_times_1890_plus_height_times_1860
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1499_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1499_times_17200_plus_image_type_times_19100_plus_width_times_1900_plus_height_times_1870
    fn = xcf_file_size_mod_1499_times_17200_plus_image_type_times_19100_plus_width_times_1900_plus_height_times_1870
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1493_importable_from_package():
    from xcf import xcf_file_size_mod_1493_times_17100_plus_image_type_times_19000_plus_width_times_1890_plus_height_times_1860
    assert callable(xcf_file_size_mod_1493_times_17100_plus_image_type_times_19000_plus_width_times_1890_plus_height_times_1860)


def test_mod1499_importable_from_package():
    from xcf import xcf_file_size_mod_1499_times_17200_plus_image_type_times_19100_plus_width_times_1900_plus_height_times_1870
    assert callable(xcf_file_size_mod_1499_times_17200_plus_image_type_times_19100_plus_width_times_1900_plus_height_times_1870)
