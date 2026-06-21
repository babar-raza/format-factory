"""Sprint 330 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_313_times_500_plus_image_type_times_3400_plus_width_times_height_times_2700,
    xcf_file_size_mod_317_times_450_plus_image_type_times_1200_plus_layer_count_times_3400,
)


# --- F1: xcf_file_size_mod_313_times_500_plus_image_type_times_3400_plus_width_times_height_times_2700 ---

class TestXcfFileSizeMod313Times500PlusImageType3400PlusWidthHeight2700:
    def test_red_returns_91200(self):
        assert xcf_file_size_mod_313_times_500_plus_image_type_times_3400_plus_width_times_height_times_2700(RED) == 91200

    def test_blue_returns_91700(self):
        assert xcf_file_size_mod_313_times_500_plus_image_type_times_3400_plus_width_times_height_times_2700(BLUE) == 91700

    def test_gray_returns_103200(self):
        assert xcf_file_size_mod_313_times_500_plus_image_type_times_3400_plus_width_times_height_times_2700(GRAY) == 103200

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_313_times_500_plus_image_type_times_3400_plus_width_times_height_times_2700(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_313_times_500_plus_image_type_times_3400_plus_width_times_height_times_2700(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_313_times_500_plus_image_type_times_3400_plus_width_times_height_times_2700(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_313_times_500_plus_image_type_times_3400_plus_width_times_height_times_2700(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_313_times_500_plus_image_type_times_3400_plus_width_times_height_times_2700(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_313_times_500_plus_image_type_times_3400_plus_width_times_height_times_2700(GRAY) >
                xcf_file_size_mod_313_times_500_plus_image_type_times_3400_plus_width_times_height_times_2700(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_313_times_500_plus_image_type_times_3400_plus_width_times_height_times_2700(str(RED)) == 91200


# --- F2: xcf_file_size_mod_317_times_450_plus_image_type_times_1200_plus_layer_count_times_3400 ---

class TestXcfFileSizeMod317Times450PlusImageType1200PlusLayerCount3400:
    def test_red_returns_83050(self):
        assert xcf_file_size_mod_317_times_450_plus_image_type_times_1200_plus_layer_count_times_3400(RED) == 83050

    def test_blue_returns_83500(self):
        assert xcf_file_size_mod_317_times_450_plus_image_type_times_1200_plus_layer_count_times_3400(BLUE) == 83500

    def test_gray_returns_84700(self):
        assert xcf_file_size_mod_317_times_450_plus_image_type_times_1200_plus_layer_count_times_3400(GRAY) == 84700

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_317_times_450_plus_image_type_times_1200_plus_layer_count_times_3400(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_317_times_450_plus_image_type_times_1200_plus_layer_count_times_3400(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_317_times_450_plus_image_type_times_1200_plus_layer_count_times_3400(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_317_times_450_plus_image_type_times_1200_plus_layer_count_times_3400(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_317_times_450_plus_image_type_times_1200_plus_layer_count_times_3400(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_317_times_450_plus_image_type_times_1200_plus_layer_count_times_3400(GRAY) >
                xcf_file_size_mod_317_times_450_plus_image_type_times_1200_plus_layer_count_times_3400(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_317_times_450_plus_image_type_times_1200_plus_layer_count_times_3400(str(RED)) == 83050
