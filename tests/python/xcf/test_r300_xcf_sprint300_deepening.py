"""Sprint 300 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_167_times_250_plus_image_type_times_2400_plus_width_times_height_times_1700,
    xcf_file_size_mod_173_times_200_plus_image_type_times_700_plus_layer_count_times_2400,
)


# --- F1: xcf_file_size_mod_167_times_250_plus_image_type_times_2400_plus_width_times_height_times_1700 ---

class TestXcfFileSizeMod167Times250PlusImageType2400PlusWidthTimesHeight1700:
    def test_red_returns_4200(self):
        assert xcf_file_size_mod_167_times_250_plus_image_type_times_2400_plus_width_times_height_times_1700(RED) == 4200

    def test_blue_returns_4450(self):
        assert xcf_file_size_mod_167_times_250_plus_image_type_times_2400_plus_width_times_height_times_1700(BLUE) == 4450

    def test_gray_returns_11950(self):
        assert xcf_file_size_mod_167_times_250_plus_image_type_times_2400_plus_width_times_height_times_1700(GRAY) == 11950

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_167_times_250_plus_image_type_times_2400_plus_width_times_height_times_1700(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_167_times_250_plus_image_type_times_2400_plus_width_times_height_times_1700(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_167_times_250_plus_image_type_times_2400_plus_width_times_height_times_1700(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_167_times_250_plus_image_type_times_2400_plus_width_times_height_times_1700(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_167_times_250_plus_image_type_times_2400_plus_width_times_height_times_1700(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_167_times_250_plus_image_type_times_2400_plus_width_times_height_times_1700(GRAY) >
                xcf_file_size_mod_167_times_250_plus_image_type_times_2400_plus_width_times_height_times_1700(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_167_times_250_plus_image_type_times_2400_plus_width_times_height_times_1700(str(RED)) == 4200


# --- F2: xcf_file_size_mod_173_times_200_plus_image_type_times_700_plus_layer_count_times_2400 ---

class TestXcfFileSizeMod173Times200PlusImageType700PlusLayerCount2400:
    def test_red_returns_3200(self):
        assert xcf_file_size_mod_173_times_200_plus_image_type_times_700_plus_layer_count_times_2400(RED) == 3200

    def test_blue_returns_3400(self):
        assert xcf_file_size_mod_173_times_200_plus_image_type_times_700_plus_layer_count_times_2400(BLUE) == 3400

    def test_gray_returns_4100(self):
        assert xcf_file_size_mod_173_times_200_plus_image_type_times_700_plus_layer_count_times_2400(GRAY) == 4100

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_173_times_200_plus_image_type_times_700_plus_layer_count_times_2400(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_173_times_200_plus_image_type_times_700_plus_layer_count_times_2400(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_173_times_200_plus_image_type_times_700_plus_layer_count_times_2400(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_173_times_200_plus_image_type_times_700_plus_layer_count_times_2400(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_173_times_200_plus_image_type_times_700_plus_layer_count_times_2400(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_173_times_200_plus_image_type_times_700_plus_layer_count_times_2400(GRAY) >
                xcf_file_size_mod_173_times_200_plus_image_type_times_700_plus_layer_count_times_2400(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_173_times_200_plus_image_type_times_700_plus_layer_count_times_2400(str(RED)) == 3200
