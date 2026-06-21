"""Sprint 420 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_691_times_1250_plus_image_type_times_6400_plus_width_times_height_times_5700,
    xcf_file_size_mod_701_times_1200_plus_image_type_times_2700_plus_layer_count_times_6400,
)


# --- F1: xcf_file_size_mod_691_times_1250_plus_image_type_times_6400_plus_width_times_height_times_5700 ---

class TestXcfFileSizeMod691Times1250PlusImageType6400PlusWidthHeight5700:
    def test_red_returns_226950(self):
        assert xcf_file_size_mod_691_times_1250_plus_image_type_times_6400_plus_width_times_height_times_5700(RED) == 226950

    def test_blue_returns_228200(self):
        assert xcf_file_size_mod_691_times_1250_plus_image_type_times_6400_plus_width_times_height_times_5700(BLUE) == 228200

    def test_gray_returns_251700(self):
        assert xcf_file_size_mod_691_times_1250_plus_image_type_times_6400_plus_width_times_height_times_5700(GRAY) == 251700

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_691_times_1250_plus_image_type_times_6400_plus_width_times_height_times_5700(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_691_times_1250_plus_image_type_times_6400_plus_width_times_height_times_5700(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_691_times_1250_plus_image_type_times_6400_plus_width_times_height_times_5700(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_691_times_1250_plus_image_type_times_6400_plus_width_times_height_times_5700(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_691_times_1250_plus_image_type_times_6400_plus_width_times_height_times_5700(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_691_times_1250_plus_image_type_times_6400_plus_width_times_height_times_5700(GRAY) >
                xcf_file_size_mod_691_times_1250_plus_image_type_times_6400_plus_width_times_height_times_5700(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_691_times_1250_plus_image_type_times_6400_plus_width_times_height_times_5700(str(RED)) == 226950


# --- F2: xcf_file_size_mod_701_times_1200_plus_image_type_times_2700_plus_layer_count_times_6400 ---

class TestXcfFileSizeMod701Times1200PlusImageType2700PlusLayerCount6400:
    def test_red_returns_218800(self):
        assert xcf_file_size_mod_701_times_1200_plus_image_type_times_2700_plus_layer_count_times_6400(RED) == 218800

    def test_blue_returns_220000(self):
        assert xcf_file_size_mod_701_times_1200_plus_image_type_times_2700_plus_layer_count_times_6400(BLUE) == 220000

    def test_gray_returns_222700(self):
        assert xcf_file_size_mod_701_times_1200_plus_image_type_times_2700_plus_layer_count_times_6400(GRAY) == 222700

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_701_times_1200_plus_image_type_times_2700_plus_layer_count_times_6400(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_701_times_1200_plus_image_type_times_2700_plus_layer_count_times_6400(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_701_times_1200_plus_image_type_times_2700_plus_layer_count_times_6400(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_701_times_1200_plus_image_type_times_2700_plus_layer_count_times_6400(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_701_times_1200_plus_image_type_times_2700_plus_layer_count_times_6400(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_701_times_1200_plus_image_type_times_2700_plus_layer_count_times_6400(GRAY) >
                xcf_file_size_mod_701_times_1200_plus_image_type_times_2700_plus_layer_count_times_6400(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_701_times_1200_plus_image_type_times_2700_plus_layer_count_times_6400(str(RED)) == 218800
