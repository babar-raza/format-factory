"""Sprint 660 XCF analytics deepening tests - primes 1531, 1543."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1531_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1531_times_17500_plus_image_type_times_19400_plus_width_times_1930_plus_height_times_1900
    assert xcf_file_size_mod_1531_times_17500_plus_image_type_times_19400_plus_width_times_1930_plus_height_times_1900(str(RED)) == 3101330


def test_mod1531_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1531_times_17500_plus_image_type_times_19400_plus_width_times_1930_plus_height_times_1900
    assert xcf_file_size_mod_1531_times_17500_plus_image_type_times_19400_plus_width_times_1930_plus_height_times_1900(str(BLUE)) == 3118830


def test_mod1531_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1531_times_17500_plus_image_type_times_19400_plus_width_times_1930_plus_height_times_1900
    assert xcf_file_size_mod_1531_times_17500_plus_image_type_times_19400_plus_width_times_1930_plus_height_times_1900(str(GRAY)) == 3142060


def test_mod1543_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1543_times_17600_plus_image_type_times_19500_plus_width_times_1940_plus_height_times_1910
    assert xcf_file_size_mod_1543_times_17600_plus_image_type_times_19500_plus_width_times_1940_plus_height_times_1910(str(RED)) == 3119050


def test_mod1543_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1543_times_17600_plus_image_type_times_19500_plus_width_times_1940_plus_height_times_1910
    assert xcf_file_size_mod_1543_times_17600_plus_image_type_times_19500_plus_width_times_1940_plus_height_times_1910(str(BLUE)) == 3136650


def test_mod1543_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1543_times_17600_plus_image_type_times_19500_plus_width_times_1940_plus_height_times_1910
    assert xcf_file_size_mod_1543_times_17600_plus_image_type_times_19500_plus_width_times_1940_plus_height_times_1910(str(GRAY)) == 3160000


def test_mod1531_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1531_times_17500_plus_image_type_times_19400_plus_width_times_1930_plus_height_times_1900
    assert isinstance(xcf_file_size_mod_1531_times_17500_plus_image_type_times_19400_plus_width_times_1930_plus_height_times_1900(str(RED)), int)


def test_mod1543_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1543_times_17600_plus_image_type_times_19500_plus_width_times_1940_plus_height_times_1910
    assert isinstance(xcf_file_size_mod_1543_times_17600_plus_image_type_times_19500_plus_width_times_1940_plus_height_times_1910(str(RED)), int)


def test_mod1531_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1531_times_17500_plus_image_type_times_19400_plus_width_times_1930_plus_height_times_1900
    assert xcf_file_size_mod_1531_times_17500_plus_image_type_times_19400_plus_width_times_1930_plus_height_times_1900(str(RED)) >= 0


def test_mod1543_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1543_times_17600_plus_image_type_times_19500_plus_width_times_1940_plus_height_times_1910
    assert xcf_file_size_mod_1543_times_17600_plus_image_type_times_19500_plus_width_times_1940_plus_height_times_1910(str(RED)) >= 0


def test_mod1531_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1531_times_17500_plus_image_type_times_19400_plus_width_times_1930_plus_height_times_1900
    fn = xcf_file_size_mod_1531_times_17500_plus_image_type_times_19400_plus_width_times_1930_plus_height_times_1900
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1543_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1543_times_17600_plus_image_type_times_19500_plus_width_times_1940_plus_height_times_1910
    fn = xcf_file_size_mod_1543_times_17600_plus_image_type_times_19500_plus_width_times_1940_plus_height_times_1910
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1531_importable_from_package():
    from xcf import xcf_file_size_mod_1531_times_17500_plus_image_type_times_19400_plus_width_times_1930_plus_height_times_1900
    assert callable(xcf_file_size_mod_1531_times_17500_plus_image_type_times_19400_plus_width_times_1930_plus_height_times_1900)


def test_mod1543_importable_from_package():
    from xcf import xcf_file_size_mod_1543_times_17600_plus_image_type_times_19500_plus_width_times_1940_plus_height_times_1910
    assert callable(xcf_file_size_mod_1543_times_17600_plus_image_type_times_19500_plus_width_times_1940_plus_height_times_1910)
