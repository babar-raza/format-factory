"""Sprint 354 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_419_times_700_plus_image_type_times_4200_plus_width_times_height_times_3500,
    xcf_file_size_mod_421_times_650_plus_image_type_times_1600_plus_layer_count_times_4200,
)


# --- F1: xcf_file_size_mod_419_times_700_plus_image_type_times_4200_plus_width_times_height_times_3500 ---

class TestXcfFileSizeMod419Times700PlusImageType4200PlusWidthHeight3500:
    def test_red_returns_127400(self):
        assert xcf_file_size_mod_419_times_700_plus_image_type_times_4200_plus_width_times_height_times_3500(RED) == 127400

    def test_blue_returns_128100(self):
        assert xcf_file_size_mod_419_times_700_plus_image_type_times_4200_plus_width_times_height_times_3500(BLUE) == 128100

    def test_gray_returns_142800(self):
        assert xcf_file_size_mod_419_times_700_plus_image_type_times_4200_plus_width_times_height_times_3500(GRAY) == 142800

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_419_times_700_plus_image_type_times_4200_plus_width_times_height_times_3500(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_419_times_700_plus_image_type_times_4200_plus_width_times_height_times_3500(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_419_times_700_plus_image_type_times_4200_plus_width_times_height_times_3500(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_419_times_700_plus_image_type_times_4200_plus_width_times_height_times_3500(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_419_times_700_plus_image_type_times_4200_plus_width_times_height_times_3500(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_419_times_700_plus_image_type_times_4200_plus_width_times_height_times_3500(GRAY) >
                xcf_file_size_mod_419_times_700_plus_image_type_times_4200_plus_width_times_height_times_3500(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_419_times_700_plus_image_type_times_4200_plus_width_times_height_times_3500(str(RED)) == 127400


# --- F2: xcf_file_size_mod_421_times_650_plus_image_type_times_1600_plus_layer_count_times_4200 ---

class TestXcfFileSizeMod421Times650PlusImageType1600PlusLayerCount4200:
    def test_red_returns_119250(self):
        assert xcf_file_size_mod_421_times_650_plus_image_type_times_1600_plus_layer_count_times_4200(RED) == 119250

    def test_blue_returns_119900(self):
        assert xcf_file_size_mod_421_times_650_plus_image_type_times_1600_plus_layer_count_times_4200(BLUE) == 119900

    def test_gray_returns_121500(self):
        assert xcf_file_size_mod_421_times_650_plus_image_type_times_1600_plus_layer_count_times_4200(GRAY) == 121500

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_421_times_650_plus_image_type_times_1600_plus_layer_count_times_4200(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_421_times_650_plus_image_type_times_1600_plus_layer_count_times_4200(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_421_times_650_plus_image_type_times_1600_plus_layer_count_times_4200(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_421_times_650_plus_image_type_times_1600_plus_layer_count_times_4200(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_421_times_650_plus_image_type_times_1600_plus_layer_count_times_4200(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_421_times_650_plus_image_type_times_1600_plus_layer_count_times_4200(GRAY) >
                xcf_file_size_mod_421_times_650_plus_image_type_times_1600_plus_layer_count_times_4200(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_421_times_650_plus_image_type_times_1600_plus_layer_count_times_4200(str(RED)) == 119250
