"""Sprint 408 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_643_times_1150_plus_image_type_times_6000_plus_width_times_height_times_5300,
    xcf_file_size_mod_647_times_1100_plus_image_type_times_2500_plus_layer_count_times_6000,
)


# --- F1: xcf_file_size_mod_643_times_1150_plus_image_type_times_6000_plus_width_times_height_times_5300 ---

class TestXcfFileSizeMod643Times1150PlusImageType6000PlusWidthHeight5300:
    def test_red_returns_208850(self):
        assert xcf_file_size_mod_643_times_1150_plus_image_type_times_6000_plus_width_times_height_times_5300(RED) == 208850

    def test_blue_returns_210000(self):
        assert xcf_file_size_mod_643_times_1150_plus_image_type_times_6000_plus_width_times_height_times_5300(BLUE) == 210000

    def test_gray_returns_231900(self):
        assert xcf_file_size_mod_643_times_1150_plus_image_type_times_6000_plus_width_times_height_times_5300(GRAY) == 231900

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_643_times_1150_plus_image_type_times_6000_plus_width_times_height_times_5300(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_643_times_1150_plus_image_type_times_6000_plus_width_times_height_times_5300(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_643_times_1150_plus_image_type_times_6000_plus_width_times_height_times_5300(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_643_times_1150_plus_image_type_times_6000_plus_width_times_height_times_5300(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_643_times_1150_plus_image_type_times_6000_plus_width_times_height_times_5300(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_643_times_1150_plus_image_type_times_6000_plus_width_times_height_times_5300(GRAY) >
                xcf_file_size_mod_643_times_1150_plus_image_type_times_6000_plus_width_times_height_times_5300(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_643_times_1150_plus_image_type_times_6000_plus_width_times_height_times_5300(str(RED)) == 208850


# --- F2: xcf_file_size_mod_647_times_1100_plus_image_type_times_2500_plus_layer_count_times_6000 ---

class TestXcfFileSizeMod647Times1100PlusImageType2500PlusLayerCount6000:
    def test_red_returns_200700(self):
        assert xcf_file_size_mod_647_times_1100_plus_image_type_times_2500_plus_layer_count_times_6000(RED) == 200700

    def test_blue_returns_201800(self):
        assert xcf_file_size_mod_647_times_1100_plus_image_type_times_2500_plus_layer_count_times_6000(BLUE) == 201800

    def test_gray_returns_204300(self):
        assert xcf_file_size_mod_647_times_1100_plus_image_type_times_2500_plus_layer_count_times_6000(GRAY) == 204300

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_647_times_1100_plus_image_type_times_2500_plus_layer_count_times_6000(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_647_times_1100_plus_image_type_times_2500_plus_layer_count_times_6000(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_647_times_1100_plus_image_type_times_2500_plus_layer_count_times_6000(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_647_times_1100_plus_image_type_times_2500_plus_layer_count_times_6000(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_647_times_1100_plus_image_type_times_2500_plus_layer_count_times_6000(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_647_times_1100_plus_image_type_times_2500_plus_layer_count_times_6000(GRAY) >
                xcf_file_size_mod_647_times_1100_plus_image_type_times_2500_plus_layer_count_times_6000(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_647_times_1100_plus_image_type_times_2500_plus_layer_count_times_6000(str(RED)) == 200700
