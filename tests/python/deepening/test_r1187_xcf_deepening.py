"""Sprint 633 XCF analytics deepening tests - primes 1423, 1427."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1423_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1423_times_15700_plus_image_type_times_17600_plus_width_times_1750_plus_height_times_1720
    assert xcf_file_size_mod_1423_times_15700_plus_image_type_times_17600_plus_width_times_1750_plus_height_times_1720(str(RED)) == 2782370


def test_mod1423_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1423_times_15700_plus_image_type_times_17600_plus_width_times_1750_plus_height_times_1720
    assert xcf_file_size_mod_1423_times_15700_plus_image_type_times_17600_plus_width_times_1750_plus_height_times_1720(str(BLUE)) == 2798070


def test_mod1423_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1423_times_15700_plus_image_type_times_17600_plus_width_times_1750_plus_height_times_1720
    assert xcf_file_size_mod_1423_times_15700_plus_image_type_times_17600_plus_width_times_1750_plus_height_times_1720(str(GRAY)) == 2819140


def test_mod1423_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1423_times_15700_plus_image_type_times_17600_plus_width_times_1750_plus_height_times_1720
    assert isinstance(xcf_file_size_mod_1423_times_15700_plus_image_type_times_17600_plus_width_times_1750_plus_height_times_1720(str(RED)), int)


def test_mod1423_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1423_times_15700_plus_image_type_times_17600_plus_width_times_1750_plus_height_times_1720
    assert xcf_file_size_mod_1423_times_15700_plus_image_type_times_17600_plus_width_times_1750_plus_height_times_1720(str(RED)) >= 0


def test_mod1423_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1423_times_15700_plus_image_type_times_17600_plus_width_times_1750_plus_height_times_1720
    fn_ref = xcf_file_size_mod_1423_times_15700_plus_image_type_times_17600_plus_width_times_1750_plus_height_times_1720
    results = {fn_ref(str(RED)), fn_ref(str(BLUE)), fn_ref(str(GRAY))}
    assert len(results) == 3


def test_mod1423_importable_from_package():
    from xcf import xcf_file_size_mod_1423_times_15700_plus_image_type_times_17600_plus_width_times_1750_plus_height_times_1720
    assert callable(xcf_file_size_mod_1423_times_15700_plus_image_type_times_17600_plus_width_times_1750_plus_height_times_1720)


def test_mod1427_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1427_times_15800_plus_image_type_times_17700_plus_width_times_1760_plus_height_times_1730
    assert xcf_file_size_mod_1427_times_15800_plus_image_type_times_17700_plus_width_times_1760_plus_height_times_1730(str(RED)) == 2800090


def test_mod1427_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1427_times_15800_plus_image_type_times_17700_plus_width_times_1760_plus_height_times_1730
    assert xcf_file_size_mod_1427_times_15800_plus_image_type_times_17700_plus_width_times_1760_plus_height_times_1730(str(BLUE)) == 2815890


def test_mod1427_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1427_times_15800_plus_image_type_times_17700_plus_width_times_1760_plus_height_times_1730
    assert xcf_file_size_mod_1427_times_15800_plus_image_type_times_17700_plus_width_times_1760_plus_height_times_1730(str(GRAY)) == 2837080


def test_mod1427_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1427_times_15800_plus_image_type_times_17700_plus_width_times_1760_plus_height_times_1730
    assert isinstance(xcf_file_size_mod_1427_times_15800_plus_image_type_times_17700_plus_width_times_1760_plus_height_times_1730(str(RED)), int)


def test_mod1427_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1427_times_15800_plus_image_type_times_17700_plus_width_times_1760_plus_height_times_1730
    assert xcf_file_size_mod_1427_times_15800_plus_image_type_times_17700_plus_width_times_1760_plus_height_times_1730(str(RED)) >= 0


def test_mod1427_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1427_times_15800_plus_image_type_times_17700_plus_width_times_1760_plus_height_times_1730
    fn_ref = xcf_file_size_mod_1427_times_15800_plus_image_type_times_17700_plus_width_times_1760_plus_height_times_1730
    results = {fn_ref(str(RED)), fn_ref(str(BLUE)), fn_ref(str(GRAY))}
    assert len(results) == 3


def test_mod1427_importable_from_package():
    from xcf import xcf_file_size_mod_1427_times_15800_plus_image_type_times_17700_plus_width_times_1760_plus_height_times_1730
    assert callable(xcf_file_size_mod_1427_times_15800_plus_image_type_times_17700_plus_width_times_1760_plus_height_times_1730)
