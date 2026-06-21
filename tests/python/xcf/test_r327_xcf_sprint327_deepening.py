"""Sprint 327 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_307_times_475_plus_image_type_times_3300_plus_width_times_height_times_2600,
    xcf_file_size_mod_311_times_425_plus_image_type_times_1150_plus_layer_count_times_3300,
)


# --- F1: xcf_file_size_mod_307_times_475_plus_image_type_times_3300_plus_width_times_height_times_2600 ---

class TestXcfFileSizeMod307Times475PlusImageType3300PlusWidthHeight2600:
    def test_red_returns_86675(self):
        assert xcf_file_size_mod_307_times_475_plus_image_type_times_3300_plus_width_times_height_times_2600(RED) == 86675

    def test_blue_returns_87150(self):
        assert xcf_file_size_mod_307_times_475_plus_image_type_times_3300_plus_width_times_height_times_2600(BLUE) == 87150

    def test_gray_returns_98250(self):
        assert xcf_file_size_mod_307_times_475_plus_image_type_times_3300_plus_width_times_height_times_2600(GRAY) == 98250

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_307_times_475_plus_image_type_times_3300_plus_width_times_height_times_2600(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_307_times_475_plus_image_type_times_3300_plus_width_times_height_times_2600(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_307_times_475_plus_image_type_times_3300_plus_width_times_height_times_2600(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_307_times_475_plus_image_type_times_3300_plus_width_times_height_times_2600(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_307_times_475_plus_image_type_times_3300_plus_width_times_height_times_2600(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_307_times_475_plus_image_type_times_3300_plus_width_times_height_times_2600(GRAY) >
                xcf_file_size_mod_307_times_475_plus_image_type_times_3300_plus_width_times_height_times_2600(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_307_times_475_plus_image_type_times_3300_plus_width_times_height_times_2600(str(RED)) == 86675


# --- F2: xcf_file_size_mod_311_times_425_plus_image_type_times_1150_plus_layer_count_times_3300 ---

class TestXcfFileSizeMod311Times425PlusImageType1150PlusLayerCount3300:
    def test_red_returns_78525(self):
        assert xcf_file_size_mod_311_times_425_plus_image_type_times_1150_plus_layer_count_times_3300(RED) == 78525

    def test_blue_returns_78950(self):
        assert xcf_file_size_mod_311_times_425_plus_image_type_times_1150_plus_layer_count_times_3300(BLUE) == 78950

    def test_gray_returns_80100(self):
        assert xcf_file_size_mod_311_times_425_plus_image_type_times_1150_plus_layer_count_times_3300(GRAY) == 80100

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_311_times_425_plus_image_type_times_1150_plus_layer_count_times_3300(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_311_times_425_plus_image_type_times_1150_plus_layer_count_times_3300(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_311_times_425_plus_image_type_times_1150_plus_layer_count_times_3300(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_311_times_425_plus_image_type_times_1150_plus_layer_count_times_3300(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_311_times_425_plus_image_type_times_1150_plus_layer_count_times_3300(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_311_times_425_plus_image_type_times_1150_plus_layer_count_times_3300(GRAY) >
                xcf_file_size_mod_311_times_425_plus_image_type_times_1150_plus_layer_count_times_3300(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_311_times_425_plus_image_type_times_1150_plus_layer_count_times_3300(str(RED)) == 78525
