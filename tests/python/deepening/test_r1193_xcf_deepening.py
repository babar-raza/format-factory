"""Sprint 639 XCF analytics deepening tests - primes 1439, 1447."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1439_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1439_times_16100_plus_image_type_times_18000_plus_width_times_1790_plus_height_times_1760
    assert xcf_file_size_mod_1439_times_16100_plus_image_type_times_18000_plus_width_times_1790_plus_height_times_1760(str(RED)) == 2853250


def test_mod1439_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1439_times_16100_plus_image_type_times_18000_plus_width_times_1790_plus_height_times_1760
    assert xcf_file_size_mod_1439_times_16100_plus_image_type_times_18000_plus_width_times_1790_plus_height_times_1760(str(BLUE)) == 2869350


def test_mod1439_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1439_times_16100_plus_image_type_times_18000_plus_width_times_1790_plus_height_times_1760
    assert xcf_file_size_mod_1439_times_16100_plus_image_type_times_18000_plus_width_times_1790_plus_height_times_1760(str(GRAY)) == 2890900


def test_mod1439_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1439_times_16100_plus_image_type_times_18000_plus_width_times_1790_plus_height_times_1760
    assert isinstance(xcf_file_size_mod_1439_times_16100_plus_image_type_times_18000_plus_width_times_1790_plus_height_times_1760(str(RED)), int)


def test_mod1439_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1439_times_16100_plus_image_type_times_18000_plus_width_times_1790_plus_height_times_1760
    assert xcf_file_size_mod_1439_times_16100_plus_image_type_times_18000_plus_width_times_1790_plus_height_times_1760(str(RED)) >= 0


def test_mod1439_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1439_times_16100_plus_image_type_times_18000_plus_width_times_1790_plus_height_times_1760
    fn_ref = xcf_file_size_mod_1439_times_16100_plus_image_type_times_18000_plus_width_times_1790_plus_height_times_1760
    results = {fn_ref(str(RED)), fn_ref(str(BLUE)), fn_ref(str(GRAY))}
    assert len(results) == 3


def test_mod1439_importable_from_package():
    from xcf import xcf_file_size_mod_1439_times_16100_plus_image_type_times_18000_plus_width_times_1790_plus_height_times_1760
    assert callable(xcf_file_size_mod_1439_times_16100_plus_image_type_times_18000_plus_width_times_1790_plus_height_times_1760)


def test_mod1447_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1447_times_16200_plus_image_type_times_18100_plus_width_times_1800_plus_height_times_1770
    assert xcf_file_size_mod_1447_times_16200_plus_image_type_times_18100_plus_width_times_1800_plus_height_times_1770(str(RED)) == 2870970


def test_mod1447_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1447_times_16200_plus_image_type_times_18100_plus_width_times_1800_plus_height_times_1770
    assert xcf_file_size_mod_1447_times_16200_plus_image_type_times_18100_plus_width_times_1800_plus_height_times_1770(str(BLUE)) == 2887170


def test_mod1447_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1447_times_16200_plus_image_type_times_18100_plus_width_times_1800_plus_height_times_1770
    assert xcf_file_size_mod_1447_times_16200_plus_image_type_times_18100_plus_width_times_1800_plus_height_times_1770(str(GRAY)) == 2908840


def test_mod1447_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1447_times_16200_plus_image_type_times_18100_plus_width_times_1800_plus_height_times_1770
    assert isinstance(xcf_file_size_mod_1447_times_16200_plus_image_type_times_18100_plus_width_times_1800_plus_height_times_1770(str(RED)), int)


def test_mod1447_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1447_times_16200_plus_image_type_times_18100_plus_width_times_1800_plus_height_times_1770
    assert xcf_file_size_mod_1447_times_16200_plus_image_type_times_18100_plus_width_times_1800_plus_height_times_1770(str(RED)) >= 0


def test_mod1447_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1447_times_16200_plus_image_type_times_18100_plus_width_times_1800_plus_height_times_1770
    fn_ref = xcf_file_size_mod_1447_times_16200_plus_image_type_times_18100_plus_width_times_1800_plus_height_times_1770
    results = {fn_ref(str(RED)), fn_ref(str(BLUE)), fn_ref(str(GRAY))}
    assert len(results) == 3


def test_mod1447_importable_from_package():
    from xcf import xcf_file_size_mod_1447_times_16200_plus_image_type_times_18100_plus_width_times_1800_plus_height_times_1770
    assert callable(xcf_file_size_mod_1447_times_16200_plus_image_type_times_18100_plus_width_times_1800_plus_height_times_1770)
