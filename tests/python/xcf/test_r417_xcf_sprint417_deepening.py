"""Sprint 417 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_677_times_1225_plus_image_type_times_6300_plus_width_times_height_times_5600,
    xcf_file_size_mod_683_times_1175_plus_image_type_times_2650_plus_layer_count_times_6300,
)


# --- F1: xcf_file_size_mod_677_times_1225_plus_image_type_times_6300_plus_width_times_height_times_5600 ---

class TestXcfFileSizeMod677Times1225PlusImageType6300PlusWidthHeight5600:
    def test_red_returns_222425(self):
        assert xcf_file_size_mod_677_times_1225_plus_image_type_times_6300_plus_width_times_height_times_5600(RED) == 222425

    def test_blue_returns_223650(self):
        assert xcf_file_size_mod_677_times_1225_plus_image_type_times_6300_plus_width_times_height_times_5600(BLUE) == 223650

    def test_gray_returns_246750(self):
        assert xcf_file_size_mod_677_times_1225_plus_image_type_times_6300_plus_width_times_height_times_5600(GRAY) == 246750

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_677_times_1225_plus_image_type_times_6300_plus_width_times_height_times_5600(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_677_times_1225_plus_image_type_times_6300_plus_width_times_height_times_5600(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_677_times_1225_plus_image_type_times_6300_plus_width_times_height_times_5600(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_677_times_1225_plus_image_type_times_6300_plus_width_times_height_times_5600(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_677_times_1225_plus_image_type_times_6300_plus_width_times_height_times_5600(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_677_times_1225_plus_image_type_times_6300_plus_width_times_height_times_5600(GRAY) >
                xcf_file_size_mod_677_times_1225_plus_image_type_times_6300_plus_width_times_height_times_5600(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_677_times_1225_plus_image_type_times_6300_plus_width_times_height_times_5600(str(RED)) == 222425


# --- F2: xcf_file_size_mod_683_times_1175_plus_image_type_times_2650_plus_layer_count_times_6300 ---

class TestXcfFileSizeMod683Times1175PlusImageType2650PlusLayerCount6300:
    def test_red_returns_214275(self):
        assert xcf_file_size_mod_683_times_1175_plus_image_type_times_2650_plus_layer_count_times_6300(RED) == 214275

    def test_blue_returns_215450(self):
        assert xcf_file_size_mod_683_times_1175_plus_image_type_times_2650_plus_layer_count_times_6300(BLUE) == 215450

    def test_gray_returns_218100(self):
        assert xcf_file_size_mod_683_times_1175_plus_image_type_times_2650_plus_layer_count_times_6300(GRAY) == 218100

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_683_times_1175_plus_image_type_times_2650_plus_layer_count_times_6300(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_683_times_1175_plus_image_type_times_2650_plus_layer_count_times_6300(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_683_times_1175_plus_image_type_times_2650_plus_layer_count_times_6300(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_683_times_1175_plus_image_type_times_2650_plus_layer_count_times_6300(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_683_times_1175_plus_image_type_times_2650_plus_layer_count_times_6300(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_683_times_1175_plus_image_type_times_2650_plus_layer_count_times_6300(GRAY) >
                xcf_file_size_mod_683_times_1175_plus_image_type_times_2650_plus_layer_count_times_6300(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_683_times_1175_plus_image_type_times_2650_plus_layer_count_times_6300(str(RED)) == 214275
