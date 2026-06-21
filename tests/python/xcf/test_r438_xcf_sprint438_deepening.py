"""Sprint 438 XCF analytics deepening tests."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_773_times_1400_plus_image_type_times_7000_plus_width_times_height_times_6300,
    xcf_file_size_mod_787_times_1350_plus_image_type_times_3000_plus_layer_count_times_7000,
)


class TestXcfFileSizeMod773Times1400PlusImageType7000PlusWidthHeight6300:
    def test_red_returns_254100(self):
        assert xcf_file_size_mod_773_times_1400_plus_image_type_times_7000_plus_width_times_height_times_6300(RED) == 254100

    def test_blue_returns_255500(self):
        assert xcf_file_size_mod_773_times_1400_plus_image_type_times_7000_plus_width_times_height_times_6300(BLUE) == 255500

    def test_gray_returns_281400(self):
        assert xcf_file_size_mod_773_times_1400_plus_image_type_times_7000_plus_width_times_height_times_6300(GRAY) == 281400

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_773_times_1400_plus_image_type_times_7000_plus_width_times_height_times_6300(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_773_times_1400_plus_image_type_times_7000_plus_width_times_height_times_6300(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_773_times_1400_plus_image_type_times_7000_plus_width_times_height_times_6300(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_773_times_1400_plus_image_type_times_7000_plus_width_times_height_times_6300(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_773_times_1400_plus_image_type_times_7000_plus_width_times_height_times_6300(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_773_times_1400_plus_image_type_times_7000_plus_width_times_height_times_6300(GRAY) >
                xcf_file_size_mod_773_times_1400_plus_image_type_times_7000_plus_width_times_height_times_6300(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_773_times_1400_plus_image_type_times_7000_plus_width_times_height_times_6300(str(RED)) == 254100


class TestXcfFileSizeMod787Times1350PlusImageType3000PlusLayerCount7000:
    def test_red_returns_245950(self):
        assert xcf_file_size_mod_787_times_1350_plus_image_type_times_3000_plus_layer_count_times_7000(RED) == 245950

    def test_blue_returns_247300(self):
        assert xcf_file_size_mod_787_times_1350_plus_image_type_times_3000_plus_layer_count_times_7000(BLUE) == 247300

    def test_gray_returns_250300(self):
        assert xcf_file_size_mod_787_times_1350_plus_image_type_times_3000_plus_layer_count_times_7000(GRAY) == 250300

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_787_times_1350_plus_image_type_times_3000_plus_layer_count_times_7000(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_787_times_1350_plus_image_type_times_3000_plus_layer_count_times_7000(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_787_times_1350_plus_image_type_times_3000_plus_layer_count_times_7000(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_787_times_1350_plus_image_type_times_3000_plus_layer_count_times_7000(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_787_times_1350_plus_image_type_times_3000_plus_layer_count_times_7000(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_787_times_1350_plus_image_type_times_3000_plus_layer_count_times_7000(GRAY) >
                xcf_file_size_mod_787_times_1350_plus_image_type_times_3000_plus_layer_count_times_7000(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_787_times_1350_plus_image_type_times_3000_plus_layer_count_times_7000(str(RED)) == 245950
