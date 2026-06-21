"""Sprint 267 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_37_times_250_plus_image_type_times_1300_plus_width_times_height_times_400,
    xcf_file_size_mod_23_times_200_plus_image_type_times_800_plus_layer_count_times_500,
)


# --- F1: xcf_file_size_mod_37_times_250_plus_image_type_times_1300_plus_width_times_height_times_400 ---

class TestXcfFileSizeMod37Times250PlusImageType1300PlusWidthHeightTimes400:
    def test_red_returns_7650(self):
        assert xcf_file_size_mod_37_times_250_plus_image_type_times_1300_plus_width_times_height_times_400(RED) == 7650

    def test_blue_returns_7900(self):
        assert xcf_file_size_mod_37_times_250_plus_image_type_times_1300_plus_width_times_height_times_400(BLUE) == 7900

    def test_gray_returns_10400(self):
        assert xcf_file_size_mod_37_times_250_plus_image_type_times_1300_plus_width_times_height_times_400(GRAY) == 10400

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_37_times_250_plus_image_type_times_1300_plus_width_times_height_times_400(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_37_times_250_plus_image_type_times_1300_plus_width_times_height_times_400(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_37_times_250_plus_image_type_times_1300_plus_width_times_height_times_400(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_37_times_250_plus_image_type_times_1300_plus_width_times_height_times_400(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_37_times_250_plus_image_type_times_1300_plus_width_times_height_times_400(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_37_times_250_plus_image_type_times_1300_plus_width_times_height_times_400(GRAY) >
                xcf_file_size_mod_37_times_250_plus_image_type_times_1300_plus_width_times_height_times_400(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_37_times_250_plus_image_type_times_1300_plus_width_times_height_times_400(str(RED)) == 7650


# --- F2: xcf_file_size_mod_23_times_200_plus_image_type_times_800_plus_layer_count_times_500 ---

class TestXcfFileSizeMod23Times200PlusImageType800PlusLayerCount500:
    def test_red_returns_3700(self):
        assert xcf_file_size_mod_23_times_200_plus_image_type_times_800_plus_layer_count_times_500(RED) == 3700

    def test_blue_returns_3900(self):
        assert xcf_file_size_mod_23_times_200_plus_image_type_times_800_plus_layer_count_times_500(BLUE) == 3900

    def test_gray_returns_4700(self):
        assert xcf_file_size_mod_23_times_200_plus_image_type_times_800_plus_layer_count_times_500(GRAY) == 4700

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_23_times_200_plus_image_type_times_800_plus_layer_count_times_500(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_23_times_200_plus_image_type_times_800_plus_layer_count_times_500(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_23_times_200_plus_image_type_times_800_plus_layer_count_times_500(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_23_times_200_plus_image_type_times_800_plus_layer_count_times_500(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_23_times_200_plus_image_type_times_800_plus_layer_count_times_500(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_23_times_200_plus_image_type_times_800_plus_layer_count_times_500(GRAY) >
                xcf_file_size_mod_23_times_200_plus_image_type_times_800_plus_layer_count_times_500(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_23_times_200_plus_image_type_times_800_plus_layer_count_times_500(str(RED)) == 3700
