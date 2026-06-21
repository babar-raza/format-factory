"""Sprint 262 — Product deepening: PBM, PPM, QOI, XCF composite analytics."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

PBM_SAMPLE = _REPO / "samples" / "by-format" / "pbm" / "valid" / "1x1-black.pbm"
PPM_SAMPLE = _REPO / "samples" / "by-format" / "ppm" / "valid" / "1x1-red.ppm"
QOI_SAMPLE = _REPO / "samples" / "by-format" / "qoi" / "valid" / "1x1-red.qoi"
XCF_SAMPLE = _REPO / "samples" / "by-format" / "xcf" / "valid" / "1x1-rgba-blue.xcf"

from src.python.pbm import (
    pbm_black_pixel_count_times_100_plus_file_size_mod_13_times_50_plus_total_pixel_count,
    pbm_width_squared_plus_height_squared_plus_file_size_times_3,
)
from src.python.ppm import (
    ppm_file_size_times_3_plus_width_squared_plus_height_squared_plus_unique_pixel_count_times_10,
    ppm_avg_red_channel_int_times_width_times_height_plus_file_size_mod_17,
)
from src.python.qoi import (
    qoi_channel_count_times_200_plus_file_size_mod_23_times_10_plus_width_times_height,
    qoi_avg_brightness_int_times_10_plus_channel_count_times_file_size_mod_7,
)
from src.python.xcf import (
    xcf_width_times_height_times_3_plus_file_size_mod_23_times_50_plus_image_type_times_200,
    xcf_file_size_mod_29_times_100_plus_image_type_times_900_plus_width_sq_plus_height_sq,
)


class TestPbmBlackPixelComposite:
    def test_returns_int(self):
        assert isinstance(pbm_black_pixel_count_times_100_plus_file_size_mod_13_times_50_plus_total_pixel_count(PBM_SAMPLE), int)

    def test_positive(self):
        assert pbm_black_pixel_count_times_100_plus_file_size_mod_13_times_50_plus_total_pixel_count(PBM_SAMPLE) > 0

    def test_deterministic(self):
        r1 = pbm_black_pixel_count_times_100_plus_file_size_mod_13_times_50_plus_total_pixel_count(PBM_SAMPLE)
        r2 = pbm_black_pixel_count_times_100_plus_file_size_mod_13_times_50_plus_total_pixel_count(PBM_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert pbm_black_pixel_count_times_100_plus_file_size_mod_13_times_50_plus_total_pixel_count(PBM_SAMPLE) == 701


class TestPbmWidthSquaredComposite:
    def test_returns_int(self):
        assert isinstance(pbm_width_squared_plus_height_squared_plus_file_size_times_3(PBM_SAMPLE), int)

    def test_positive(self):
        assert pbm_width_squared_plus_height_squared_plus_file_size_times_3(PBM_SAMPLE) > 0

    def test_deterministic(self):
        r1 = pbm_width_squared_plus_height_squared_plus_file_size_times_3(PBM_SAMPLE)
        r2 = pbm_width_squared_plus_height_squared_plus_file_size_times_3(PBM_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert pbm_width_squared_plus_height_squared_plus_file_size_times_3(PBM_SAMPLE) == 38


class TestPpmFileSizeComposite:
    def test_returns_int(self):
        assert isinstance(ppm_file_size_times_3_plus_width_squared_plus_height_squared_plus_unique_pixel_count_times_10(PPM_SAMPLE), int)

    def test_positive(self):
        assert ppm_file_size_times_3_plus_width_squared_plus_height_squared_plus_unique_pixel_count_times_10(PPM_SAMPLE) > 0

    def test_deterministic(self):
        r1 = ppm_file_size_times_3_plus_width_squared_plus_height_squared_plus_unique_pixel_count_times_10(PPM_SAMPLE)
        r2 = ppm_file_size_times_3_plus_width_squared_plus_height_squared_plus_unique_pixel_count_times_10(PPM_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert ppm_file_size_times_3_plus_width_squared_plus_height_squared_plus_unique_pixel_count_times_10(PPM_SAMPLE) == 69


class TestPpmAvgRedComposite:
    def test_returns_int(self):
        assert isinstance(ppm_avg_red_channel_int_times_width_times_height_plus_file_size_mod_17(PPM_SAMPLE), int)

    def test_positive(self):
        assert ppm_avg_red_channel_int_times_width_times_height_plus_file_size_mod_17(PPM_SAMPLE) > 0

    def test_deterministic(self):
        r1 = ppm_avg_red_channel_int_times_width_times_height_plus_file_size_mod_17(PPM_SAMPLE)
        r2 = ppm_avg_red_channel_int_times_width_times_height_plus_file_size_mod_17(PPM_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert ppm_avg_red_channel_int_times_width_times_height_plus_file_size_mod_17(PPM_SAMPLE) == 257


class TestQoiChannelComposite:
    def test_returns_int(self):
        assert isinstance(qoi_channel_count_times_200_plus_file_size_mod_23_times_10_plus_width_times_height(QOI_SAMPLE), int)

    def test_positive(self):
        assert qoi_channel_count_times_200_plus_file_size_mod_23_times_10_plus_width_times_height(QOI_SAMPLE) > 0

    def test_deterministic(self):
        r1 = qoi_channel_count_times_200_plus_file_size_mod_23_times_10_plus_width_times_height(QOI_SAMPLE)
        r2 = qoi_channel_count_times_200_plus_file_size_mod_23_times_10_plus_width_times_height(QOI_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert qoi_channel_count_times_200_plus_file_size_mod_23_times_10_plus_width_times_height(QOI_SAMPLE) == 841


class TestQoiBrightnessComposite:
    def test_returns_int(self):
        assert isinstance(qoi_avg_brightness_int_times_10_plus_channel_count_times_file_size_mod_7(QOI_SAMPLE), int)

    def test_positive(self):
        assert qoi_avg_brightness_int_times_10_plus_channel_count_times_file_size_mod_7(QOI_SAMPLE) > 0

    def test_deterministic(self):
        r1 = qoi_avg_brightness_int_times_10_plus_channel_count_times_file_size_mod_7(QOI_SAMPLE)
        r2 = qoi_avg_brightness_int_times_10_plus_channel_count_times_file_size_mod_7(QOI_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert qoi_avg_brightness_int_times_10_plus_channel_count_times_file_size_mod_7(QOI_SAMPLE) == 2574


class TestXcfWidthHeightComposite:
    def test_returns_int(self):
        assert isinstance(xcf_width_times_height_times_3_plus_file_size_mod_23_times_50_plus_image_type_times_200(XCF_SAMPLE), int)

    def test_positive(self):
        assert xcf_width_times_height_times_3_plus_file_size_mod_23_times_50_plus_image_type_times_200(XCF_SAMPLE) > 0

    def test_deterministic(self):
        r1 = xcf_width_times_height_times_3_plus_file_size_mod_23_times_50_plus_image_type_times_200(XCF_SAMPLE)
        r2 = xcf_width_times_height_times_3_plus_file_size_mod_23_times_50_plus_image_type_times_200(XCF_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert xcf_width_times_height_times_3_plus_file_size_mod_23_times_50_plus_image_type_times_200(XCF_SAMPLE) == 853


class TestXcfFileSizeMod29Composite:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_29_times_100_plus_image_type_times_900_plus_width_sq_plus_height_sq(XCF_SAMPLE), int)

    def test_positive(self):
        assert xcf_file_size_mod_29_times_100_plus_image_type_times_900_plus_width_sq_plus_height_sq(XCF_SAMPLE) > 0

    def test_deterministic(self):
        r1 = xcf_file_size_mod_29_times_100_plus_image_type_times_900_plus_width_sq_plus_height_sq(XCF_SAMPLE)
        r2 = xcf_file_size_mod_29_times_100_plus_image_type_times_900_plus_width_sq_plus_height_sq(XCF_SAMPLE)
        assert r1 == r2

    def test_expected_value(self):
        assert xcf_file_size_mod_29_times_100_plus_image_type_times_900_plus_width_sq_plus_height_sq(XCF_SAMPLE) == 402
