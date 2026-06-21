"""Sprint 266 deepening – PBM / PPM / QOI / XCF composite analytics."""
import sys, pathlib, pytest

_REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.pbm import (
    pbm_black_pixel_count_times_200_plus_file_size_mod_17_times_100_plus_wh_times_50,
    pbm_wh_times_500_plus_black_pixel_count_times_300_plus_file_size_times_2,
)
from src.python.ppm import (
    ppm_wh_times_500_plus_unique_pixel_count_times_300_plus_file_size_times_3,
    ppm_avg_red_int_times_200_plus_wh_times_100_plus_file_size_mod_19_times_50,
)
from src.python.qoi import (
    qoi_channel_count_times_300_plus_file_size_mod_19_times_200_plus_wh_times_100,
    qoi_avg_brightness_int_times_100_plus_channel_times_file_size_mod_11_times_10,
)
from src.python.xcf import (
    xcf_wh_times_400_plus_image_type_times_300_plus_file_size_mod_31_times_100,
    xcf_file_size_mod_37_times_200_plus_image_type_times_800_plus_wh_squared,
)

_SAMPLES = _REPO / "samples" / "by-format"
_PBM = _SAMPLES / "pbm" / "valid" / "1x1-black.pbm"
_PPM = _SAMPLES / "ppm" / "valid" / "1x1-red.ppm"
_QOI = _SAMPLES / "qoi" / "valid" / "1x1-red.qoi"
_XCF = _SAMPLES / "xcf" / "valid" / "1x1-rgba-blue.xcf"


# --- PBM f1 ---
class TestPbmF1:
    def test_returns_int(self):
        assert isinstance(pbm_black_pixel_count_times_200_plus_file_size_mod_17_times_100_plus_wh_times_50(str(_PBM)), int)

    def test_positive(self):
        assert pbm_black_pixel_count_times_200_plus_file_size_mod_17_times_100_plus_wh_times_50(str(_PBM)) > 0

    def test_deterministic(self):
        a = pbm_black_pixel_count_times_200_plus_file_size_mod_17_times_100_plus_wh_times_50(str(_PBM))
        b = pbm_black_pixel_count_times_200_plus_file_size_mod_17_times_100_plus_wh_times_50(str(_PBM))
        assert a == b

    def test_expected(self):
        assert pbm_black_pixel_count_times_200_plus_file_size_mod_17_times_100_plus_wh_times_50(str(_PBM)) == 1450


# --- PBM f2 ---
class TestPbmF2:
    def test_returns_int(self):
        assert isinstance(pbm_wh_times_500_plus_black_pixel_count_times_300_plus_file_size_times_2(str(_PBM)), int)

    def test_positive(self):
        assert pbm_wh_times_500_plus_black_pixel_count_times_300_plus_file_size_times_2(str(_PBM)) > 0

    def test_deterministic(self):
        a = pbm_wh_times_500_plus_black_pixel_count_times_300_plus_file_size_times_2(str(_PBM))
        b = pbm_wh_times_500_plus_black_pixel_count_times_300_plus_file_size_times_2(str(_PBM))
        assert a == b

    def test_expected(self):
        assert pbm_wh_times_500_plus_black_pixel_count_times_300_plus_file_size_times_2(str(_PBM)) == 824


# --- PPM f3 ---
class TestPpmF3:
    def test_returns_int(self):
        assert isinstance(ppm_wh_times_500_plus_unique_pixel_count_times_300_plus_file_size_times_3(str(_PPM)), int)

    def test_positive(self):
        assert ppm_wh_times_500_plus_unique_pixel_count_times_300_plus_file_size_times_3(str(_PPM)) > 0

    def test_deterministic(self):
        a = ppm_wh_times_500_plus_unique_pixel_count_times_300_plus_file_size_times_3(str(_PPM))
        b = ppm_wh_times_500_plus_unique_pixel_count_times_300_plus_file_size_times_3(str(_PPM))
        assert a == b

    def test_expected(self):
        assert ppm_wh_times_500_plus_unique_pixel_count_times_300_plus_file_size_times_3(str(_PPM)) == 857


# --- PPM f4 ---
class TestPpmF4:
    def test_returns_int(self):
        assert isinstance(ppm_avg_red_int_times_200_plus_wh_times_100_plus_file_size_mod_19_times_50(str(_PPM)), int)

    def test_positive(self):
        assert ppm_avg_red_int_times_200_plus_wh_times_100_plus_file_size_mod_19_times_50(str(_PPM)) > 0

    def test_deterministic(self):
        a = ppm_avg_red_int_times_200_plus_wh_times_100_plus_file_size_mod_19_times_50(str(_PPM))
        b = ppm_avg_red_int_times_200_plus_wh_times_100_plus_file_size_mod_19_times_50(str(_PPM))
        assert a == b

    def test_expected(self):
        assert ppm_avg_red_int_times_200_plus_wh_times_100_plus_file_size_mod_19_times_50(str(_PPM)) == 51100


# --- QOI f5 ---
class TestQoiF5:
    def test_returns_int(self):
        assert isinstance(qoi_channel_count_times_300_plus_file_size_mod_19_times_200_plus_wh_times_100(str(_QOI)), int)

    def test_positive(self):
        assert qoi_channel_count_times_300_plus_file_size_mod_19_times_200_plus_wh_times_100(str(_QOI)) > 0

    def test_deterministic(self):
        a = qoi_channel_count_times_300_plus_file_size_mod_19_times_200_plus_wh_times_100(str(_QOI))
        b = qoi_channel_count_times_300_plus_file_size_mod_19_times_200_plus_wh_times_100(str(_QOI))
        assert a == b

    def test_expected(self):
        assert qoi_channel_count_times_300_plus_file_size_mod_19_times_200_plus_wh_times_100(str(_QOI)) == 2900


# --- QOI f6 ---
class TestQoiF6:
    def test_returns_int(self):
        assert isinstance(qoi_avg_brightness_int_times_100_plus_channel_times_file_size_mod_11_times_10(str(_QOI)), int)

    def test_positive(self):
        assert qoi_avg_brightness_int_times_100_plus_channel_times_file_size_mod_11_times_10(str(_QOI)) > 0

    def test_deterministic(self):
        a = qoi_avg_brightness_int_times_100_plus_channel_times_file_size_mod_11_times_10(str(_QOI))
        b = qoi_avg_brightness_int_times_100_plus_channel_times_file_size_mod_11_times_10(str(_QOI))
        assert a == b

    def test_expected(self):
        assert qoi_avg_brightness_int_times_100_plus_channel_times_file_size_mod_11_times_10(str(_QOI)) == 25700


# --- XCF f7 ---
class TestXcfF7:
    def test_returns_int(self):
        assert isinstance(xcf_wh_times_400_plus_image_type_times_300_plus_file_size_mod_31_times_100(str(_XCF)), int)

    def test_positive(self):
        assert xcf_wh_times_400_plus_image_type_times_300_plus_file_size_mod_31_times_100(str(_XCF)) > 0

    def test_deterministic(self):
        a = xcf_wh_times_400_plus_image_type_times_300_plus_file_size_mod_31_times_100(str(_XCF))
        b = xcf_wh_times_400_plus_image_type_times_300_plus_file_size_mod_31_times_100(str(_XCF))
        assert a == b

    def test_expected(self):
        assert xcf_wh_times_400_plus_image_type_times_300_plus_file_size_mod_31_times_100(str(_XCF)) == 2700


# --- XCF f8 ---
class TestXcfF8:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_37_times_200_plus_image_type_times_800_plus_wh_squared(str(_XCF)), int)

    def test_positive(self):
        assert xcf_file_size_mod_37_times_200_plus_image_type_times_800_plus_wh_squared(str(_XCF)) > 0

    def test_deterministic(self):
        a = xcf_file_size_mod_37_times_200_plus_image_type_times_800_plus_wh_squared(str(_XCF))
        b = xcf_file_size_mod_37_times_200_plus_image_type_times_800_plus_wh_squared(str(_XCF))
        assert a == b

    def test_expected(self):
        assert xcf_file_size_mod_37_times_200_plus_image_type_times_800_plus_wh_squared(str(_XCF)) == 6002
