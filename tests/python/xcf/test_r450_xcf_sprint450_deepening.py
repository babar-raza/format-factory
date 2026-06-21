"""Sprint 450 XCF analytics deepening tests."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_829_times_1600_plus_image_type_times_7800_plus_width_times_height_times_6700,
    xcf_file_size_mod_839_times_1550_plus_image_type_times_3400_plus_layer_count_times_7800,
)


class TestXcfFileSizeMod829Times1600PlusImageType7800PlusWidthHeight6700:
    def test_red_returns_289900(self):
        assert xcf_file_size_mod_829_times_1600_plus_image_type_times_7800_plus_width_times_height_times_6700(RED) == 289900

    def test_blue_returns_291500(self):
        assert xcf_file_size_mod_829_times_1600_plus_image_type_times_7800_plus_width_times_height_times_6700(BLUE) == 291500

    def test_gray_returns_319400(self):
        assert xcf_file_size_mod_829_times_1600_plus_image_type_times_7800_plus_width_times_height_times_6700(GRAY) == 319400

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_829_times_1600_plus_image_type_times_7800_plus_width_times_height_times_6700(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_829_times_1600_plus_image_type_times_7800_plus_width_times_height_times_6700(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_829_times_1600_plus_image_type_times_7800_plus_width_times_height_times_6700(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_829_times_1600_plus_image_type_times_7800_plus_width_times_height_times_6700(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_829_times_1600_plus_image_type_times_7800_plus_width_times_height_times_6700(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_829_times_1600_plus_image_type_times_7800_plus_width_times_height_times_6700(GRAY) >
                xcf_file_size_mod_829_times_1600_plus_image_type_times_7800_plus_width_times_height_times_6700(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_829_times_1600_plus_image_type_times_7800_plus_width_times_height_times_6700(str(RED)) == 289900


class TestXcfFileSizeMod839Times1550PlusImageType3400PlusLayerCount7800:
    def test_red_returns_282150(self):
        assert xcf_file_size_mod_839_times_1550_plus_image_type_times_3400_plus_layer_count_times_7800(RED) == 282150

    def test_blue_returns_283700(self):
        assert xcf_file_size_mod_839_times_1550_plus_image_type_times_3400_plus_layer_count_times_7800(BLUE) == 283700

    def test_gray_returns_287100(self):
        assert xcf_file_size_mod_839_times_1550_plus_image_type_times_3400_plus_layer_count_times_7800(GRAY) == 287100

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_839_times_1550_plus_image_type_times_3400_plus_layer_count_times_7800(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_839_times_1550_plus_image_type_times_3400_plus_layer_count_times_7800(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_839_times_1550_plus_image_type_times_3400_plus_layer_count_times_7800(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_839_times_1550_plus_image_type_times_3400_plus_layer_count_times_7800(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_839_times_1550_plus_image_type_times_3400_plus_layer_count_times_7800(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_839_times_1550_plus_image_type_times_3400_plus_layer_count_times_7800(GRAY) >
                xcf_file_size_mod_839_times_1550_plus_image_type_times_3400_plus_layer_count_times_7800(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_839_times_1550_plus_image_type_times_3400_plus_layer_count_times_7800(str(RED)) == 282150
