"""Sprint 621 XCF analytics deepening tests - primes 1321, 1327."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1321_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1321_times_14900_plus_image_type_times_16800_plus_width_times_1670_plus_height_times_1640
    assert xcf_file_size_mod_1321_times_14900_plus_image_type_times_16800_plus_width_times_1670_plus_height_times_1640(str(RED)) == 2640610

def test_mod1321_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1321_times_14900_plus_image_type_times_16800_plus_width_times_1670_plus_height_times_1640
    assert xcf_file_size_mod_1321_times_14900_plus_image_type_times_16800_plus_width_times_1670_plus_height_times_1640(str(BLUE)) == 2655510

def test_mod1321_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1321_times_14900_plus_image_type_times_16800_plus_width_times_1670_plus_height_times_1640
    assert xcf_file_size_mod_1321_times_14900_plus_image_type_times_16800_plus_width_times_1670_plus_height_times_1640(str(GRAY)) == 2675620

def test_mod1327_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1327_times_15000_plus_image_type_times_16900_plus_width_times_1680_plus_height_times_1650
    assert xcf_file_size_mod_1327_times_15000_plus_image_type_times_16900_plus_width_times_1680_plus_height_times_1650(str(RED)) == 2658330

def test_mod1327_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1327_times_15000_plus_image_type_times_16900_plus_width_times_1680_plus_height_times_1650
    assert xcf_file_size_mod_1327_times_15000_plus_image_type_times_16900_plus_width_times_1680_plus_height_times_1650(str(BLUE)) == 2673330

def test_mod1327_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1327_times_15000_plus_image_type_times_16900_plus_width_times_1680_plus_height_times_1650
    assert xcf_file_size_mod_1327_times_15000_plus_image_type_times_16900_plus_width_times_1680_plus_height_times_1650(str(GRAY)) == 2693560

def test_mod1321_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1321_times_14900_plus_image_type_times_16800_plus_width_times_1670_plus_height_times_1640
    assert isinstance(xcf_file_size_mod_1321_times_14900_plus_image_type_times_16800_plus_width_times_1670_plus_height_times_1640(str(RED)), int)

def test_mod1327_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1327_times_15000_plus_image_type_times_16900_plus_width_times_1680_plus_height_times_1650
    assert isinstance(xcf_file_size_mod_1327_times_15000_plus_image_type_times_16900_plus_width_times_1680_plus_height_times_1650(str(RED)), int)

def test_mod1321_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1321_times_14900_plus_image_type_times_16800_plus_width_times_1670_plus_height_times_1640
    assert xcf_file_size_mod_1321_times_14900_plus_image_type_times_16800_plus_width_times_1670_plus_height_times_1640(str(RED)) >= 0

def test_mod1327_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1327_times_15000_plus_image_type_times_16900_plus_width_times_1680_plus_height_times_1650
    assert xcf_file_size_mod_1327_times_15000_plus_image_type_times_16900_plus_width_times_1680_plus_height_times_1650(str(RED)) >= 0

def test_mod1321_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1321_times_14900_plus_image_type_times_16800_plus_width_times_1670_plus_height_times_1640
    fn = xcf_file_size_mod_1321_times_14900_plus_image_type_times_16800_plus_width_times_1670_plus_height_times_1640
    assert len({fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}) == 3

def test_mod1327_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1327_times_15000_plus_image_type_times_16900_plus_width_times_1680_plus_height_times_1650
    fn = xcf_file_size_mod_1327_times_15000_plus_image_type_times_16900_plus_width_times_1680_plus_height_times_1650
    assert len({fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}) == 3

def test_mod1321_importable_from_package():
    from xcf import xcf_file_size_mod_1321_times_14900_plus_image_type_times_16800_plus_width_times_1670_plus_height_times_1640
    assert callable(xcf_file_size_mod_1321_times_14900_plus_image_type_times_16800_plus_width_times_1670_plus_height_times_1640)

def test_mod1327_importable_from_package():
    from xcf import xcf_file_size_mod_1327_times_15000_plus_image_type_times_16900_plus_width_times_1680_plus_height_times_1650
    assert callable(xcf_file_size_mod_1327_times_15000_plus_image_type_times_16900_plus_width_times_1680_plus_height_times_1650)
