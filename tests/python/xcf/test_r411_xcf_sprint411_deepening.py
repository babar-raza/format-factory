"""Sprint 411 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_653_times_1175_plus_image_type_times_6100_plus_width_times_height_times_5400,
    xcf_file_size_mod_659_times_1125_plus_image_type_times_2550_plus_layer_count_times_6100,
)


# --- F1: xcf_file_size_mod_653_times_1175_plus_image_type_times_6100_plus_width_times_height_times_5400 ---

class TestXcfFileSizeMod653Times1175PlusImageType6100PlusWidthHeight5400:
    def test_red_returns_213375(self):
        assert xcf_file_size_mod_653_times_1175_plus_image_type_times_6100_plus_width_times_height_times_5400(RED) == 213375

    def test_blue_returns_214550(self):
        assert xcf_file_size_mod_653_times_1175_plus_image_type_times_6100_plus_width_times_height_times_5400(BLUE) == 214550

    def test_gray_returns_236850(self):
        assert xcf_file_size_mod_653_times_1175_plus_image_type_times_6100_plus_width_times_height_times_5400(GRAY) == 236850

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_653_times_1175_plus_image_type_times_6100_plus_width_times_height_times_5400(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_653_times_1175_plus_image_type_times_6100_plus_width_times_height_times_5400(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_653_times_1175_plus_image_type_times_6100_plus_width_times_height_times_5400(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_653_times_1175_plus_image_type_times_6100_plus_width_times_height_times_5400(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_653_times_1175_plus_image_type_times_6100_plus_width_times_height_times_5400(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_653_times_1175_plus_image_type_times_6100_plus_width_times_height_times_5400(GRAY) >
                xcf_file_size_mod_653_times_1175_plus_image_type_times_6100_plus_width_times_height_times_5400(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_653_times_1175_plus_image_type_times_6100_plus_width_times_height_times_5400(str(RED)) == 213375


# --- F2: xcf_file_size_mod_659_times_1125_plus_image_type_times_2550_plus_layer_count_times_6100 ---

class TestXcfFileSizeMod659Times1125PlusImageType2550PlusLayerCount6100:
    def test_red_returns_205225(self):
        assert xcf_file_size_mod_659_times_1125_plus_image_type_times_2550_plus_layer_count_times_6100(RED) == 205225

    def test_blue_returns_206350(self):
        assert xcf_file_size_mod_659_times_1125_plus_image_type_times_2550_plus_layer_count_times_6100(BLUE) == 206350

    def test_gray_returns_208900(self):
        assert xcf_file_size_mod_659_times_1125_plus_image_type_times_2550_plus_layer_count_times_6100(GRAY) == 208900

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_659_times_1125_plus_image_type_times_2550_plus_layer_count_times_6100(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_659_times_1125_plus_image_type_times_2550_plus_layer_count_times_6100(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_659_times_1125_plus_image_type_times_2550_plus_layer_count_times_6100(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_659_times_1125_plus_image_type_times_2550_plus_layer_count_times_6100(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_659_times_1125_plus_image_type_times_2550_plus_layer_count_times_6100(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_659_times_1125_plus_image_type_times_2550_plus_layer_count_times_6100(GRAY) >
                xcf_file_size_mod_659_times_1125_plus_image_type_times_2550_plus_layer_count_times_6100(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_659_times_1125_plus_image_type_times_2550_plus_layer_count_times_6100(str(RED)) == 205225
