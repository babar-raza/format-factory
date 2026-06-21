"""Sprint 405 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_631_times_1125_plus_image_type_times_5900_plus_width_times_height_times_5200,
    xcf_file_size_mod_641_times_1075_plus_image_type_times_2450_plus_layer_count_times_5900,
)


# --- F1: xcf_file_size_mod_631_times_1125_plus_image_type_times_5900_plus_width_times_height_times_5200 ---

class TestXcfFileSizeMod631Times1125PlusImageType5900PlusWidthHeight5200:
    def test_red_returns_204325(self):
        assert xcf_file_size_mod_631_times_1125_plus_image_type_times_5900_plus_width_times_height_times_5200(RED) == 204325

    def test_blue_returns_205450(self):
        assert xcf_file_size_mod_631_times_1125_plus_image_type_times_5900_plus_width_times_height_times_5200(BLUE) == 205450

    def test_gray_returns_226950(self):
        assert xcf_file_size_mod_631_times_1125_plus_image_type_times_5900_plus_width_times_height_times_5200(GRAY) == 226950

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_631_times_1125_plus_image_type_times_5900_plus_width_times_height_times_5200(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_631_times_1125_plus_image_type_times_5900_plus_width_times_height_times_5200(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_631_times_1125_plus_image_type_times_5900_plus_width_times_height_times_5200(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_631_times_1125_plus_image_type_times_5900_plus_width_times_height_times_5200(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_631_times_1125_plus_image_type_times_5900_plus_width_times_height_times_5200(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_631_times_1125_plus_image_type_times_5900_plus_width_times_height_times_5200(GRAY) >
                xcf_file_size_mod_631_times_1125_plus_image_type_times_5900_plus_width_times_height_times_5200(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_631_times_1125_plus_image_type_times_5900_plus_width_times_height_times_5200(str(RED)) == 204325


# --- F2: xcf_file_size_mod_641_times_1075_plus_image_type_times_2450_plus_layer_count_times_5900 ---

class TestXcfFileSizeMod641Times1075PlusImageType2450PlusLayerCount5900:
    def test_red_returns_196175(self):
        assert xcf_file_size_mod_641_times_1075_plus_image_type_times_2450_plus_layer_count_times_5900(RED) == 196175

    def test_blue_returns_197250(self):
        assert xcf_file_size_mod_641_times_1075_plus_image_type_times_2450_plus_layer_count_times_5900(BLUE) == 197250

    def test_gray_returns_199700(self):
        assert xcf_file_size_mod_641_times_1075_plus_image_type_times_2450_plus_layer_count_times_5900(GRAY) == 199700

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_641_times_1075_plus_image_type_times_2450_plus_layer_count_times_5900(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_641_times_1075_plus_image_type_times_2450_plus_layer_count_times_5900(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_641_times_1075_plus_image_type_times_2450_plus_layer_count_times_5900(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_641_times_1075_plus_image_type_times_2450_plus_layer_count_times_5900(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_641_times_1075_plus_image_type_times_2450_plus_layer_count_times_5900(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_641_times_1075_plus_image_type_times_2450_plus_layer_count_times_5900(GRAY) >
                xcf_file_size_mod_641_times_1075_plus_image_type_times_2450_plus_layer_count_times_5900(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_641_times_1075_plus_image_type_times_2450_plus_layer_count_times_5900(str(RED)) == 196175
