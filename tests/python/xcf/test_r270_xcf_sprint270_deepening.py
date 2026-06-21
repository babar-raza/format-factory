"""Sprint 270 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_43_times_300_plus_image_type_times_1400_plus_width_times_height_times_600,
    xcf_file_size_mod_29_times_250_plus_image_type_times_1100_plus_layer_count_times_800,
)


# --- F1: xcf_file_size_mod_43_times_300_plus_image_type_times_1400_plus_width_times_height_times_600 ---

class TestXcfFileSizeMod43Times300PlusImageType1400PlusWidthHeightTimes600:
    def test_red_returns_2100(self):
        assert xcf_file_size_mod_43_times_300_plus_image_type_times_1400_plus_width_times_height_times_600(RED) == 2100

    def test_blue_returns_2400(self):
        assert xcf_file_size_mod_43_times_300_plus_image_type_times_1400_plus_width_times_height_times_600(BLUE) == 2400

    def test_gray_returns_5600(self):
        assert xcf_file_size_mod_43_times_300_plus_image_type_times_1400_plus_width_times_height_times_600(GRAY) == 5600

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_43_times_300_plus_image_type_times_1400_plus_width_times_height_times_600(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_43_times_300_plus_image_type_times_1400_plus_width_times_height_times_600(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_43_times_300_plus_image_type_times_1400_plus_width_times_height_times_600(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_43_times_300_plus_image_type_times_1400_plus_width_times_height_times_600(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_43_times_300_plus_image_type_times_1400_plus_width_times_height_times_600(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_43_times_300_plus_image_type_times_1400_plus_width_times_height_times_600(GRAY) >
                xcf_file_size_mod_43_times_300_plus_image_type_times_1400_plus_width_times_height_times_600(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_43_times_300_plus_image_type_times_1400_plus_width_times_height_times_600(str(RED)) == 2100


# --- F2: xcf_file_size_mod_29_times_250_plus_image_type_times_1100_plus_layer_count_times_800 ---

class TestXcfFileSizeMod29Times250PlusImageType1100PlusLayerCount800:
    def test_red_returns_1550(self):
        assert xcf_file_size_mod_29_times_250_plus_image_type_times_1100_plus_layer_count_times_800(RED) == 1550

    def test_blue_returns_1800(self):
        assert xcf_file_size_mod_29_times_250_plus_image_type_times_1100_plus_layer_count_times_800(BLUE) == 1800

    def test_gray_returns_2900(self):
        assert xcf_file_size_mod_29_times_250_plus_image_type_times_1100_plus_layer_count_times_800(GRAY) == 2900

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_29_times_250_plus_image_type_times_1100_plus_layer_count_times_800(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_29_times_250_plus_image_type_times_1100_plus_layer_count_times_800(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_29_times_250_plus_image_type_times_1100_plus_layer_count_times_800(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_29_times_250_plus_image_type_times_1100_plus_layer_count_times_800(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_29_times_250_plus_image_type_times_1100_plus_layer_count_times_800(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_29_times_250_plus_image_type_times_1100_plus_layer_count_times_800(GRAY) >
                xcf_file_size_mod_29_times_250_plus_image_type_times_1100_plus_layer_count_times_800(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_29_times_250_plus_image_type_times_1100_plus_layer_count_times_800(str(RED)) == 1550
