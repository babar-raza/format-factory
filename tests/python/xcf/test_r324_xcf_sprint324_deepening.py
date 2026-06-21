"""Sprint 324 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_283_times_450_plus_image_type_times_3200_plus_width_times_height_times_2500,
    xcf_file_size_mod_293_times_400_plus_image_type_times_1100_plus_layer_count_times_3200,
)


# --- F1: xcf_file_size_mod_283_times_450_plus_image_type_times_3200_plus_width_times_height_times_2500 ---

class TestXcfFileSizeMod283Times450PlusImageType3200PlusWidthHeight2500:
    def test_red_returns_82150(self):
        assert xcf_file_size_mod_283_times_450_plus_image_type_times_3200_plus_width_times_height_times_2500(RED) == 82150

    def test_blue_returns_82600(self):
        assert xcf_file_size_mod_283_times_450_plus_image_type_times_3200_plus_width_times_height_times_2500(BLUE) == 82600

    def test_gray_returns_93300(self):
        assert xcf_file_size_mod_283_times_450_plus_image_type_times_3200_plus_width_times_height_times_2500(GRAY) == 93300

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_283_times_450_plus_image_type_times_3200_plus_width_times_height_times_2500(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_283_times_450_plus_image_type_times_3200_plus_width_times_height_times_2500(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_283_times_450_plus_image_type_times_3200_plus_width_times_height_times_2500(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_283_times_450_plus_image_type_times_3200_plus_width_times_height_times_2500(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_283_times_450_plus_image_type_times_3200_plus_width_times_height_times_2500(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_283_times_450_plus_image_type_times_3200_plus_width_times_height_times_2500(GRAY) >
                xcf_file_size_mod_283_times_450_plus_image_type_times_3200_plus_width_times_height_times_2500(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_283_times_450_plus_image_type_times_3200_plus_width_times_height_times_2500(str(RED)) == 82150


# --- F2: xcf_file_size_mod_293_times_400_plus_image_type_times_1100_plus_layer_count_times_3200 ---

class TestXcfFileSizeMod293Times400PlusImageType1100PlusLayerCount3200:
    def test_red_returns_74000(self):
        assert xcf_file_size_mod_293_times_400_plus_image_type_times_1100_plus_layer_count_times_3200(RED) == 74000

    def test_blue_returns_74400(self):
        assert xcf_file_size_mod_293_times_400_plus_image_type_times_1100_plus_layer_count_times_3200(BLUE) == 74400

    def test_gray_returns_75500(self):
        assert xcf_file_size_mod_293_times_400_plus_image_type_times_1100_plus_layer_count_times_3200(GRAY) == 75500

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_293_times_400_plus_image_type_times_1100_plus_layer_count_times_3200(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_293_times_400_plus_image_type_times_1100_plus_layer_count_times_3200(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_293_times_400_plus_image_type_times_1100_plus_layer_count_times_3200(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_293_times_400_plus_image_type_times_1100_plus_layer_count_times_3200(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_293_times_400_plus_image_type_times_1100_plus_layer_count_times_3200(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_293_times_400_plus_image_type_times_1100_plus_layer_count_times_3200(GRAY) >
                xcf_file_size_mod_293_times_400_plus_image_type_times_1100_plus_layer_count_times_3200(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_293_times_400_plus_image_type_times_1100_plus_layer_count_times_3200(str(RED)) == 74000
