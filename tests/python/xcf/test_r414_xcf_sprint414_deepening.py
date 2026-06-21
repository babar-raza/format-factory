"""Sprint 414 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_661_times_1200_plus_image_type_times_6200_plus_width_times_height_times_5500,
    xcf_file_size_mod_673_times_1150_plus_image_type_times_2600_plus_layer_count_times_6200,
)


# --- F1: xcf_file_size_mod_661_times_1200_plus_image_type_times_6200_plus_width_times_height_times_5500 ---

class TestXcfFileSizeMod661Times1200PlusImageType6200PlusWidthHeight5500:
    def test_red_returns_217900(self):
        assert xcf_file_size_mod_661_times_1200_plus_image_type_times_6200_plus_width_times_height_times_5500(RED) == 217900

    def test_blue_returns_219100(self):
        assert xcf_file_size_mod_661_times_1200_plus_image_type_times_6200_plus_width_times_height_times_5500(BLUE) == 219100

    def test_gray_returns_241800(self):
        assert xcf_file_size_mod_661_times_1200_plus_image_type_times_6200_plus_width_times_height_times_5500(GRAY) == 241800

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_661_times_1200_plus_image_type_times_6200_plus_width_times_height_times_5500(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_661_times_1200_plus_image_type_times_6200_plus_width_times_height_times_5500(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_661_times_1200_plus_image_type_times_6200_plus_width_times_height_times_5500(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_661_times_1200_plus_image_type_times_6200_plus_width_times_height_times_5500(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_661_times_1200_plus_image_type_times_6200_plus_width_times_height_times_5500(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_661_times_1200_plus_image_type_times_6200_plus_width_times_height_times_5500(GRAY) >
                xcf_file_size_mod_661_times_1200_plus_image_type_times_6200_plus_width_times_height_times_5500(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_661_times_1200_plus_image_type_times_6200_plus_width_times_height_times_5500(str(RED)) == 217900


# --- F2: xcf_file_size_mod_673_times_1150_plus_image_type_times_2600_plus_layer_count_times_6200 ---

class TestXcfFileSizeMod673Times1150PlusImageType2600PlusLayerCount6200:
    def test_red_returns_209750(self):
        assert xcf_file_size_mod_673_times_1150_plus_image_type_times_2600_plus_layer_count_times_6200(RED) == 209750

    def test_blue_returns_210900(self):
        assert xcf_file_size_mod_673_times_1150_plus_image_type_times_2600_plus_layer_count_times_6200(BLUE) == 210900

    def test_gray_returns_213500(self):
        assert xcf_file_size_mod_673_times_1150_plus_image_type_times_2600_plus_layer_count_times_6200(GRAY) == 213500

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_673_times_1150_plus_image_type_times_2600_plus_layer_count_times_6200(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_673_times_1150_plus_image_type_times_2600_plus_layer_count_times_6200(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_673_times_1150_plus_image_type_times_2600_plus_layer_count_times_6200(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_673_times_1150_plus_image_type_times_2600_plus_layer_count_times_6200(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_673_times_1150_plus_image_type_times_2600_plus_layer_count_times_6200(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_673_times_1150_plus_image_type_times_2600_plus_layer_count_times_6200(GRAY) >
                xcf_file_size_mod_673_times_1150_plus_image_type_times_2600_plus_layer_count_times_6200(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_673_times_1150_plus_image_type_times_2600_plus_layer_count_times_6200(str(RED)) == 209750
