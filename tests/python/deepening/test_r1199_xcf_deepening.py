"""Sprint 645 XCF analytics deepening tests - primes 1459, 1471."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1459_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1459_times_16500_plus_image_type_times_18400_plus_width_times_1830_plus_height_times_1800
    assert xcf_file_size_mod_1459_times_16500_plus_image_type_times_18400_plus_width_times_1830_plus_height_times_1800(str(RED)) == 2924130


def test_mod1459_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1459_times_16500_plus_image_type_times_18400_plus_width_times_1830_plus_height_times_1800
    assert xcf_file_size_mod_1459_times_16500_plus_image_type_times_18400_plus_width_times_1830_plus_height_times_1800(str(BLUE)) == 2940630


def test_mod1459_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1459_times_16500_plus_image_type_times_18400_plus_width_times_1830_plus_height_times_1800
    assert xcf_file_size_mod_1459_times_16500_plus_image_type_times_18400_plus_width_times_1830_plus_height_times_1800(str(GRAY)) == 2962660


def test_mod1471_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1471_times_16600_plus_image_type_times_18500_plus_width_times_1840_plus_height_times_1810
    assert xcf_file_size_mod_1471_times_16600_plus_image_type_times_18500_plus_width_times_1840_plus_height_times_1810(str(RED)) == 2941850


def test_mod1471_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1471_times_16600_plus_image_type_times_18500_plus_width_times_1840_plus_height_times_1810
    assert xcf_file_size_mod_1471_times_16600_plus_image_type_times_18500_plus_width_times_1840_plus_height_times_1810(str(BLUE)) == 2958450


def test_mod1471_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1471_times_16600_plus_image_type_times_18500_plus_width_times_1840_plus_height_times_1810
    assert xcf_file_size_mod_1471_times_16600_plus_image_type_times_18500_plus_width_times_1840_plus_height_times_1810(str(GRAY)) == 2980600


def test_mod1459_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1459_times_16500_plus_image_type_times_18400_plus_width_times_1830_plus_height_times_1800
    assert isinstance(xcf_file_size_mod_1459_times_16500_plus_image_type_times_18400_plus_width_times_1830_plus_height_times_1800(str(RED)), int)


def test_mod1471_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1471_times_16600_plus_image_type_times_18500_plus_width_times_1840_plus_height_times_1810
    assert isinstance(xcf_file_size_mod_1471_times_16600_plus_image_type_times_18500_plus_width_times_1840_plus_height_times_1810(str(RED)), int)


def test_mod1459_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1459_times_16500_plus_image_type_times_18400_plus_width_times_1830_plus_height_times_1800
    assert xcf_file_size_mod_1459_times_16500_plus_image_type_times_18400_plus_width_times_1830_plus_height_times_1800(str(RED)) >= 0


def test_mod1471_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1471_times_16600_plus_image_type_times_18500_plus_width_times_1840_plus_height_times_1810
    assert xcf_file_size_mod_1471_times_16600_plus_image_type_times_18500_plus_width_times_1840_plus_height_times_1810(str(RED)) >= 0


def test_mod1459_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1459_times_16500_plus_image_type_times_18400_plus_width_times_1830_plus_height_times_1800
    fn = xcf_file_size_mod_1459_times_16500_plus_image_type_times_18400_plus_width_times_1830_plus_height_times_1800
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1471_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1471_times_16600_plus_image_type_times_18500_plus_width_times_1840_plus_height_times_1810
    fn = xcf_file_size_mod_1471_times_16600_plus_image_type_times_18500_plus_width_times_1840_plus_height_times_1810
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1459_importable_from_package():
    from xcf import xcf_file_size_mod_1459_times_16500_plus_image_type_times_18400_plus_width_times_1830_plus_height_times_1800
    assert callable(xcf_file_size_mod_1459_times_16500_plus_image_type_times_18400_plus_width_times_1830_plus_height_times_1800)


def test_mod1471_importable_from_package():
    from xcf import xcf_file_size_mod_1471_times_16600_plus_image_type_times_18500_plus_width_times_1840_plus_height_times_1810
    assert callable(xcf_file_size_mod_1471_times_16600_plus_image_type_times_18500_plus_width_times_1840_plus_height_times_1810)
