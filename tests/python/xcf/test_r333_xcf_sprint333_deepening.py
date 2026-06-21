"""Sprint 333 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_331_times_525_plus_image_type_times_3500_plus_width_times_height_times_2800,
    xcf_file_size_mod_337_times_475_plus_image_type_times_1250_plus_layer_count_times_3500,
)


# --- F1: xcf_file_size_mod_331_times_525_plus_image_type_times_3500_plus_width_times_height_times_2800 ---

class TestXcfFileSizeMod331Times525PlusImageType3500PlusWidthHeight2800:
    def test_red_returns_95725(self):
        assert xcf_file_size_mod_331_times_525_plus_image_type_times_3500_plus_width_times_height_times_2800(RED) == 95725

    def test_blue_returns_96250(self):
        assert xcf_file_size_mod_331_times_525_plus_image_type_times_3500_plus_width_times_height_times_2800(BLUE) == 96250

    def test_gray_returns_108150(self):
        assert xcf_file_size_mod_331_times_525_plus_image_type_times_3500_plus_width_times_height_times_2800(GRAY) == 108150

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_331_times_525_plus_image_type_times_3500_plus_width_times_height_times_2800(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_331_times_525_plus_image_type_times_3500_plus_width_times_height_times_2800(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_331_times_525_plus_image_type_times_3500_plus_width_times_height_times_2800(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_331_times_525_plus_image_type_times_3500_plus_width_times_height_times_2800(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_331_times_525_plus_image_type_times_3500_plus_width_times_height_times_2800(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_331_times_525_plus_image_type_times_3500_plus_width_times_height_times_2800(GRAY) >
                xcf_file_size_mod_331_times_525_plus_image_type_times_3500_plus_width_times_height_times_2800(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_331_times_525_plus_image_type_times_3500_plus_width_times_height_times_2800(str(RED)) == 95725


# --- F2: xcf_file_size_mod_337_times_475_plus_image_type_times_1250_plus_layer_count_times_3500 ---

class TestXcfFileSizeMod337Times475PlusImageType1250PlusLayerCount3500:
    def test_red_returns_87575(self):
        assert xcf_file_size_mod_337_times_475_plus_image_type_times_1250_plus_layer_count_times_3500(RED) == 87575

    def test_blue_returns_88050(self):
        assert xcf_file_size_mod_337_times_475_plus_image_type_times_1250_plus_layer_count_times_3500(BLUE) == 88050

    def test_gray_returns_89300(self):
        assert xcf_file_size_mod_337_times_475_plus_image_type_times_1250_plus_layer_count_times_3500(GRAY) == 89300

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_337_times_475_plus_image_type_times_1250_plus_layer_count_times_3500(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_337_times_475_plus_image_type_times_1250_plus_layer_count_times_3500(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_337_times_475_plus_image_type_times_1250_plus_layer_count_times_3500(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_337_times_475_plus_image_type_times_1250_plus_layer_count_times_3500(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_337_times_475_plus_image_type_times_1250_plus_layer_count_times_3500(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_337_times_475_plus_image_type_times_1250_plus_layer_count_times_3500(GRAY) >
                xcf_file_size_mod_337_times_475_plus_image_type_times_1250_plus_layer_count_times_3500(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_337_times_475_plus_image_type_times_1250_plus_layer_count_times_3500(str(RED)) == 87575
