"""Sprint 615 XCF analytics deepening tests - primes 1301, 1303."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1301_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1301_times_14500_plus_image_type_times_16400_plus_width_times_1630_plus_height_times_1600
    assert xcf_file_size_mod_1301_times_14500_plus_image_type_times_16400_plus_width_times_1630_plus_height_times_1600(str(RED)) == 2569730


def test_mod1301_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1301_times_14500_plus_image_type_times_16400_plus_width_times_1630_plus_height_times_1600
    assert xcf_file_size_mod_1301_times_14500_plus_image_type_times_16400_plus_width_times_1630_plus_height_times_1600(str(BLUE)) == 2584230


def test_mod1301_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1301_times_14500_plus_image_type_times_16400_plus_width_times_1630_plus_height_times_1600
    assert xcf_file_size_mod_1301_times_14500_plus_image_type_times_16400_plus_width_times_1630_plus_height_times_1600(str(GRAY)) == 2603860


def test_mod1303_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1303_times_14600_plus_image_type_times_16500_plus_width_times_1640_plus_height_times_1610
    assert xcf_file_size_mod_1303_times_14600_plus_image_type_times_16500_plus_width_times_1640_plus_height_times_1610(str(RED)) == 2587450


def test_mod1303_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1303_times_14600_plus_image_type_times_16500_plus_width_times_1640_plus_height_times_1610
    assert xcf_file_size_mod_1303_times_14600_plus_image_type_times_16500_plus_width_times_1640_plus_height_times_1610(str(BLUE)) == 2602050


def test_mod1303_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1303_times_14600_plus_image_type_times_16500_plus_width_times_1640_plus_height_times_1610
    assert xcf_file_size_mod_1303_times_14600_plus_image_type_times_16500_plus_width_times_1640_plus_height_times_1610(str(GRAY)) == 2621800


def test_mod1301_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1301_times_14500_plus_image_type_times_16400_plus_width_times_1630_plus_height_times_1600
    assert isinstance(xcf_file_size_mod_1301_times_14500_plus_image_type_times_16400_plus_width_times_1630_plus_height_times_1600(str(RED)), int)


def test_mod1303_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1303_times_14600_plus_image_type_times_16500_plus_width_times_1640_plus_height_times_1610
    assert isinstance(xcf_file_size_mod_1303_times_14600_plus_image_type_times_16500_plus_width_times_1640_plus_height_times_1610(str(RED)), int)


def test_mod1301_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1301_times_14500_plus_image_type_times_16400_plus_width_times_1630_plus_height_times_1600
    assert xcf_file_size_mod_1301_times_14500_plus_image_type_times_16400_plus_width_times_1630_plus_height_times_1600(str(RED)) >= 0


def test_mod1303_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1303_times_14600_plus_image_type_times_16500_plus_width_times_1640_plus_height_times_1610
    assert xcf_file_size_mod_1303_times_14600_plus_image_type_times_16500_plus_width_times_1640_plus_height_times_1610(str(RED)) >= 0


def test_mod1301_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1301_times_14500_plus_image_type_times_16400_plus_width_times_1630_plus_height_times_1600
    fn = xcf_file_size_mod_1301_times_14500_plus_image_type_times_16400_plus_width_times_1630_plus_height_times_1600
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1303_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1303_times_14600_plus_image_type_times_16500_plus_width_times_1640_plus_height_times_1610
    fn = xcf_file_size_mod_1303_times_14600_plus_image_type_times_16500_plus_width_times_1640_plus_height_times_1610
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1301_importable_from_package():
    from xcf import xcf_file_size_mod_1301_times_14500_plus_image_type_times_16400_plus_width_times_1630_plus_height_times_1600
    assert callable(xcf_file_size_mod_1301_times_14500_plus_image_type_times_16400_plus_width_times_1630_plus_height_times_1600)


def test_mod1303_importable_from_package():
    from xcf import xcf_file_size_mod_1303_times_14600_plus_image_type_times_16500_plus_width_times_1640_plus_height_times_1610
    assert callable(xcf_file_size_mod_1303_times_14600_plus_image_type_times_16500_plus_width_times_1640_plus_height_times_1610)
