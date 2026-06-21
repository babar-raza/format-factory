"""Sprint 618 XCF analytics deepening tests - primes 1307, 1319."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1307_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1307_times_14700_plus_image_type_times_16600_plus_width_times_1650_plus_height_times_1620
    assert xcf_file_size_mod_1307_times_14700_plus_image_type_times_16600_plus_width_times_1650_plus_height_times_1620(str(RED)) == 2605170


def test_mod1307_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1307_times_14700_plus_image_type_times_16600_plus_width_times_1650_plus_height_times_1620
    assert xcf_file_size_mod_1307_times_14700_plus_image_type_times_16600_plus_width_times_1650_plus_height_times_1620(str(BLUE)) == 2619870


def test_mod1307_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1307_times_14700_plus_image_type_times_16600_plus_width_times_1650_plus_height_times_1620
    assert xcf_file_size_mod_1307_times_14700_plus_image_type_times_16600_plus_width_times_1650_plus_height_times_1620(str(GRAY)) == 2639740


def test_mod1319_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1319_times_14800_plus_image_type_times_16700_plus_width_times_1660_plus_height_times_1630
    assert xcf_file_size_mod_1319_times_14800_plus_image_type_times_16700_plus_width_times_1660_plus_height_times_1630(str(RED)) == 2622890


def test_mod1319_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1319_times_14800_plus_image_type_times_16700_plus_width_times_1660_plus_height_times_1630
    assert xcf_file_size_mod_1319_times_14800_plus_image_type_times_16700_plus_width_times_1660_plus_height_times_1630(str(BLUE)) == 2637690


def test_mod1319_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1319_times_14800_plus_image_type_times_16700_plus_width_times_1660_plus_height_times_1630
    assert xcf_file_size_mod_1319_times_14800_plus_image_type_times_16700_plus_width_times_1660_plus_height_times_1630(str(GRAY)) == 2657680


def test_mod1307_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1307_times_14700_plus_image_type_times_16600_plus_width_times_1650_plus_height_times_1620
    assert isinstance(xcf_file_size_mod_1307_times_14700_plus_image_type_times_16600_plus_width_times_1650_plus_height_times_1620(str(RED)), int)


def test_mod1319_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1319_times_14800_plus_image_type_times_16700_plus_width_times_1660_plus_height_times_1630
    assert isinstance(xcf_file_size_mod_1319_times_14800_plus_image_type_times_16700_plus_width_times_1660_plus_height_times_1630(str(RED)), int)


def test_mod1307_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1307_times_14700_plus_image_type_times_16600_plus_width_times_1650_plus_height_times_1620
    assert xcf_file_size_mod_1307_times_14700_plus_image_type_times_16600_plus_width_times_1650_plus_height_times_1620(str(RED)) >= 0


def test_mod1319_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1319_times_14800_plus_image_type_times_16700_plus_width_times_1660_plus_height_times_1630
    assert xcf_file_size_mod_1319_times_14800_plus_image_type_times_16700_plus_width_times_1660_plus_height_times_1630(str(RED)) >= 0


def test_mod1307_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1307_times_14700_plus_image_type_times_16600_plus_width_times_1650_plus_height_times_1620
    fn = xcf_file_size_mod_1307_times_14700_plus_image_type_times_16600_plus_width_times_1650_plus_height_times_1620
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1319_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1319_times_14800_plus_image_type_times_16700_plus_width_times_1660_plus_height_times_1630
    fn = xcf_file_size_mod_1319_times_14800_plus_image_type_times_16700_plus_width_times_1660_plus_height_times_1630
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1307_importable_from_package():
    from xcf import xcf_file_size_mod_1307_times_14700_plus_image_type_times_16600_plus_width_times_1650_plus_height_times_1620
    assert callable(xcf_file_size_mod_1307_times_14700_plus_image_type_times_16600_plus_width_times_1650_plus_height_times_1620)


def test_mod1319_importable_from_package():
    from xcf import xcf_file_size_mod_1319_times_14800_plus_image_type_times_16700_plus_width_times_1660_plus_height_times_1630
    assert callable(xcf_file_size_mod_1319_times_14800_plus_image_type_times_16700_plus_width_times_1660_plus_height_times_1630)
