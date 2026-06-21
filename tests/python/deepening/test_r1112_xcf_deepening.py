"""Sprint 558 XCF analytics deepening tests - primes 1033, 1039."""
from pathlib import Path

SAMPLES = Path("samples/by-format/xcf/valid")
RED = SAMPLES / "1x1-red-rgb.xcf"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


def test_mod1033_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1033_times_10700_plus_image_type_times_12600_plus_width_times_1250_plus_height_times_1220
    assert xcf_file_size_mod_1033_times_10700_plus_image_type_times_12600_plus_width_times_1250_plus_height_times_1220(str(RED)) == 1896370


def test_mod1033_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1033_times_10700_plus_image_type_times_12600_plus_width_times_1250_plus_height_times_1220
    assert xcf_file_size_mod_1033_times_10700_plus_image_type_times_12600_plus_width_times_1250_plus_height_times_1220(str(BLUE)) == 1907070


def test_mod1033_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1033_times_10700_plus_image_type_times_12600_plus_width_times_1250_plus_height_times_1220
    assert xcf_file_size_mod_1033_times_10700_plus_image_type_times_12600_plus_width_times_1250_plus_height_times_1220(str(GRAY)) == 1922140


def test_mod1039_red():
    from xcf.xcf_analytics import xcf_file_size_mod_1039_times_10800_plus_image_type_times_12700_plus_width_times_1260_plus_height_times_1230
    assert xcf_file_size_mod_1039_times_10800_plus_image_type_times_12700_plus_width_times_1260_plus_height_times_1230(str(RED)) == 1914090


def test_mod1039_blue():
    from xcf.xcf_analytics import xcf_file_size_mod_1039_times_10800_plus_image_type_times_12700_plus_width_times_1260_plus_height_times_1230
    assert xcf_file_size_mod_1039_times_10800_plus_image_type_times_12700_plus_width_times_1260_plus_height_times_1230(str(BLUE)) == 1924890


def test_mod1039_gray():
    from xcf.xcf_analytics import xcf_file_size_mod_1039_times_10800_plus_image_type_times_12700_plus_width_times_1260_plus_height_times_1230
    assert xcf_file_size_mod_1039_times_10800_plus_image_type_times_12700_plus_width_times_1260_plus_height_times_1230(str(GRAY)) == 1940080


def test_mod1033_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1033_times_10700_plus_image_type_times_12600_plus_width_times_1250_plus_height_times_1220
    assert isinstance(xcf_file_size_mod_1033_times_10700_plus_image_type_times_12600_plus_width_times_1250_plus_height_times_1220(str(RED)), int)


def test_mod1039_returns_int():
    from xcf.xcf_analytics import xcf_file_size_mod_1039_times_10800_plus_image_type_times_12700_plus_width_times_1260_plus_height_times_1230
    assert isinstance(xcf_file_size_mod_1039_times_10800_plus_image_type_times_12700_plus_width_times_1260_plus_height_times_1230(str(RED)), int)


def test_mod1033_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1033_times_10700_plus_image_type_times_12600_plus_width_times_1250_plus_height_times_1220
    assert xcf_file_size_mod_1033_times_10700_plus_image_type_times_12600_plus_width_times_1250_plus_height_times_1220(str(RED)) >= 0


def test_mod1039_nonnegative():
    from xcf.xcf_analytics import xcf_file_size_mod_1039_times_10800_plus_image_type_times_12700_plus_width_times_1260_plus_height_times_1230
    assert xcf_file_size_mod_1039_times_10800_plus_image_type_times_12700_plus_width_times_1260_plus_height_times_1230(str(RED)) >= 0


def test_mod1033_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1033_times_10700_plus_image_type_times_12600_plus_width_times_1250_plus_height_times_1220
    fn = xcf_file_size_mod_1033_times_10700_plus_image_type_times_12600_plus_width_times_1250_plus_height_times_1220
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1039_all_samples_differ():
    from xcf.xcf_analytics import xcf_file_size_mod_1039_times_10800_plus_image_type_times_12700_plus_width_times_1260_plus_height_times_1230
    fn = xcf_file_size_mod_1039_times_10800_plus_image_type_times_12700_plus_width_times_1260_plus_height_times_1230
    results = {fn(str(RED)), fn(str(BLUE)), fn(str(GRAY))}
    assert len(results) == 3


def test_mod1033_importable_from_package():
    from xcf import xcf_file_size_mod_1033_times_10700_plus_image_type_times_12600_plus_width_times_1250_plus_height_times_1220
    assert callable(xcf_file_size_mod_1033_times_10700_plus_image_type_times_12600_plus_width_times_1250_plus_height_times_1220)


def test_mod1039_importable_from_package():
    from xcf import xcf_file_size_mod_1039_times_10800_plus_image_type_times_12700_plus_width_times_1260_plus_height_times_1230
    assert callable(xcf_file_size_mod_1039_times_10800_plus_image_type_times_12700_plus_width_times_1260_plus_height_times_1230)
