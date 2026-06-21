"""Sprint 651 XCF analytics deepening tests - primes 1487, 1489."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1487_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1487_times_16900_plus_image_type_times_18800_plus_width_times_1870_plus_height_times_1840
    assert xcf_file_size_mod_1487_times_16900_plus_image_type_times_18800_plus_width_times_1870_plus_height_times_1840(str(RED)) == 2995010


def test_mod1487_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1487_times_16900_plus_image_type_times_18800_plus_width_times_1870_plus_height_times_1840
    assert xcf_file_size_mod_1487_times_16900_plus_image_type_times_18800_plus_width_times_1870_plus_height_times_1840(str(BLUE)) == 3011910


def test_mod1487_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1487_times_16900_plus_image_type_times_18800_plus_width_times_1870_plus_height_times_1840
    assert xcf_file_size_mod_1487_times_16900_plus_image_type_times_18800_plus_width_times_1870_plus_height_times_1840(str(GRAY)) == 3034420


def test_mod1489_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1489_times_17000_plus_image_type_times_18900_plus_width_times_1880_plus_height_times_1850
    assert xcf_file_size_mod_1489_times_17000_plus_image_type_times_18900_plus_width_times_1880_plus_height_times_1850(str(RED)) == 3012730


def test_mod1489_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1489_times_17000_plus_image_type_times_18900_plus_width_times_1880_plus_height_times_1850
    assert xcf_file_size_mod_1489_times_17000_plus_image_type_times_18900_plus_width_times_1880_plus_height_times_1850(str(BLUE)) == 3029730


def test_mod1489_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1489_times_17000_plus_image_type_times_18900_plus_width_times_1880_plus_height_times_1850
    assert xcf_file_size_mod_1489_times_17000_plus_image_type_times_18900_plus_width_times_1880_plus_height_times_1850(str(GRAY)) == 3052360


def test_mod1487_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1487_times_16900_plus_image_type_times_18800_plus_width_times_1870_plus_height_times_1840
    assert isinstance(xcf_file_size_mod_1487_times_16900_plus_image_type_times_18800_plus_width_times_1870_plus_height_times_1840(str(RED)), int)


def test_mod1489_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1489_times_17000_plus_image_type_times_18900_plus_width_times_1880_plus_height_times_1850
    assert isinstance(xcf_file_size_mod_1489_times_17000_plus_image_type_times_18900_plus_width_times_1880_plus_height_times_1850(str(RED)), int)


def test_mod1487_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1487_times_16900_plus_image_type_times_18800_plus_width_times_1870_plus_height_times_1840
    assert xcf_file_size_mod_1487_times_16900_plus_image_type_times_18800_plus_width_times_1870_plus_height_times_1840(str(RED)) >= 0


def test_mod1489_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1489_times_17000_plus_image_type_times_18900_plus_width_times_1880_plus_height_times_1850
    assert xcf_file_size_mod_1489_times_17000_plus_image_type_times_18900_plus_width_times_1880_plus_height_times_1850(str(RED)) >= 0


def test_mod1487_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1487_times_16900_plus_image_type_times_18800_plus_width_times_1870_plus_height_times_1840
    fn = xcf_file_size_mod_1487_times_16900_plus_image_type_times_18800_plus_width_times_1870_plus_height_times_1840
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1489_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1489_times_17000_plus_image_type_times_18900_plus_width_times_1880_plus_height_times_1850
    fn = xcf_file_size_mod_1489_times_17000_plus_image_type_times_18900_plus_width_times_1880_plus_height_times_1850
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1487_importable_from_package():
    from xcf import xcf_file_size_mod_1487_times_16900_plus_image_type_times_18800_plus_width_times_1870_plus_height_times_1840
    assert callable(xcf_file_size_mod_1487_times_16900_plus_image_type_times_18800_plus_width_times_1870_plus_height_times_1840)


def test_mod1489_importable_from_package():
    from xcf import xcf_file_size_mod_1489_times_17000_plus_image_type_times_18900_plus_width_times_1880_plus_height_times_1850
    assert callable(xcf_file_size_mod_1489_times_17000_plus_image_type_times_18900_plus_width_times_1880_plus_height_times_1850)
