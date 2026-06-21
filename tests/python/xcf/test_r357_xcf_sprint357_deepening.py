"""Sprint 357 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_431_times_725_plus_image_type_times_4300_plus_width_times_height_times_3600,
    xcf_file_size_mod_433_times_675_plus_image_type_times_1650_plus_layer_count_times_4300,
)


# --- F1: xcf_file_size_mod_431_times_725_plus_image_type_times_4300_plus_width_times_height_times_3600 ---

class TestXcfFileSizeMod431Times725PlusImageType4300PlusWidthHeight3600:
    def test_red_returns_131925(self):
        assert xcf_file_size_mod_431_times_725_plus_image_type_times_4300_plus_width_times_height_times_3600(RED) == 131925

    def test_blue_returns_132650(self):
        assert xcf_file_size_mod_431_times_725_plus_image_type_times_4300_plus_width_times_height_times_3600(BLUE) == 132650

    def test_gray_returns_147750(self):
        assert xcf_file_size_mod_431_times_725_plus_image_type_times_4300_plus_width_times_height_times_3600(GRAY) == 147750

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_431_times_725_plus_image_type_times_4300_plus_width_times_height_times_3600(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_431_times_725_plus_image_type_times_4300_plus_width_times_height_times_3600(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_431_times_725_plus_image_type_times_4300_plus_width_times_height_times_3600(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_431_times_725_plus_image_type_times_4300_plus_width_times_height_times_3600(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_431_times_725_plus_image_type_times_4300_plus_width_times_height_times_3600(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_431_times_725_plus_image_type_times_4300_plus_width_times_height_times_3600(GRAY) >
                xcf_file_size_mod_431_times_725_plus_image_type_times_4300_plus_width_times_height_times_3600(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_431_times_725_plus_image_type_times_4300_plus_width_times_height_times_3600(str(RED)) == 131925


# --- F2: xcf_file_size_mod_433_times_675_plus_image_type_times_1650_plus_layer_count_times_4300 ---

class TestXcfFileSizeMod433Times675PlusImageType1650PlusLayerCount4300:
    def test_red_returns_123775(self):
        assert xcf_file_size_mod_433_times_675_plus_image_type_times_1650_plus_layer_count_times_4300(RED) == 123775

    def test_blue_returns_124450(self):
        assert xcf_file_size_mod_433_times_675_plus_image_type_times_1650_plus_layer_count_times_4300(BLUE) == 124450

    def test_gray_returns_126100(self):
        assert xcf_file_size_mod_433_times_675_plus_image_type_times_1650_plus_layer_count_times_4300(GRAY) == 126100

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_433_times_675_plus_image_type_times_1650_plus_layer_count_times_4300(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_433_times_675_plus_image_type_times_1650_plus_layer_count_times_4300(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_433_times_675_plus_image_type_times_1650_plus_layer_count_times_4300(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_433_times_675_plus_image_type_times_1650_plus_layer_count_times_4300(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_433_times_675_plus_image_type_times_1650_plus_layer_count_times_4300(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_433_times_675_plus_image_type_times_1650_plus_layer_count_times_4300(GRAY) >
                xcf_file_size_mod_433_times_675_plus_image_type_times_1650_plus_layer_count_times_4300(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_433_times_675_plus_image_type_times_1650_plus_layer_count_times_4300(str(RED)) == 123775
