"""Sprint 648 XCF analytics deepening tests - primes 1481, 1483."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1481_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1481_times_16700_plus_image_type_times_18600_plus_width_times_1850_plus_height_times_1820
    assert xcf_file_size_mod_1481_times_16700_plus_image_type_times_18600_plus_width_times_1850_plus_height_times_1820(str(RED)) == 2959570


def test_mod1481_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1481_times_16700_plus_image_type_times_18600_plus_width_times_1850_plus_height_times_1820
    assert xcf_file_size_mod_1481_times_16700_plus_image_type_times_18600_plus_width_times_1850_plus_height_times_1820(str(BLUE)) == 2976270


def test_mod1481_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1481_times_16700_plus_image_type_times_18600_plus_width_times_1850_plus_height_times_1820
    assert xcf_file_size_mod_1481_times_16700_plus_image_type_times_18600_plus_width_times_1850_plus_height_times_1820(str(GRAY)) == 2998540


def test_mod1483_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1483_times_16800_plus_image_type_times_18700_plus_width_times_1860_plus_height_times_1830
    assert xcf_file_size_mod_1483_times_16800_plus_image_type_times_18700_plus_width_times_1860_plus_height_times_1830(str(RED)) == 2977290


def test_mod1483_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1483_times_16800_plus_image_type_times_18700_plus_width_times_1860_plus_height_times_1830
    assert xcf_file_size_mod_1483_times_16800_plus_image_type_times_18700_plus_width_times_1860_plus_height_times_1830(str(BLUE)) == 2994090


def test_mod1483_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1483_times_16800_plus_image_type_times_18700_plus_width_times_1860_plus_height_times_1830
    assert xcf_file_size_mod_1483_times_16800_plus_image_type_times_18700_plus_width_times_1860_plus_height_times_1830(str(GRAY)) == 3016480


def test_mod1481_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1481_times_16700_plus_image_type_times_18600_plus_width_times_1850_plus_height_times_1820
    assert isinstance(xcf_file_size_mod_1481_times_16700_plus_image_type_times_18600_plus_width_times_1850_plus_height_times_1820(str(RED)), int)


def test_mod1483_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1483_times_16800_plus_image_type_times_18700_plus_width_times_1860_plus_height_times_1830
    assert isinstance(xcf_file_size_mod_1483_times_16800_plus_image_type_times_18700_plus_width_times_1860_plus_height_times_1830(str(RED)), int)


def test_mod1481_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1481_times_16700_plus_image_type_times_18600_plus_width_times_1850_plus_height_times_1820
    assert xcf_file_size_mod_1481_times_16700_plus_image_type_times_18600_plus_width_times_1850_plus_height_times_1820(str(RED)) >= 0


def test_mod1483_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1483_times_16800_plus_image_type_times_18700_plus_width_times_1860_plus_height_times_1830
    assert xcf_file_size_mod_1483_times_16800_plus_image_type_times_18700_plus_width_times_1860_plus_height_times_1830(str(RED)) >= 0


def test_mod1481_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1481_times_16700_plus_image_type_times_18600_plus_width_times_1850_plus_height_times_1820
    fn = xcf_file_size_mod_1481_times_16700_plus_image_type_times_18600_plus_width_times_1850_plus_height_times_1820
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1483_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1483_times_16800_plus_image_type_times_18700_plus_width_times_1860_plus_height_times_1830
    fn = xcf_file_size_mod_1483_times_16800_plus_image_type_times_18700_plus_width_times_1860_plus_height_times_1830
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1481_importable_from_package():
    from xcf import xcf_file_size_mod_1481_times_16700_plus_image_type_times_18600_plus_width_times_1850_plus_height_times_1820
    assert callable(xcf_file_size_mod_1481_times_16700_plus_image_type_times_18600_plus_width_times_1850_plus_height_times_1820)


def test_mod1483_importable_from_package():
    from xcf import xcf_file_size_mod_1483_times_16800_plus_image_type_times_18700_plus_width_times_1860_plus_height_times_1830
    assert callable(xcf_file_size_mod_1483_times_16800_plus_image_type_times_18700_plus_width_times_1860_plus_height_times_1830)
