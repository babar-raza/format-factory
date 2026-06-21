"""Sprint 348 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_389_times_650_plus_image_type_times_4000_plus_width_times_height_times_3300,
    xcf_file_size_mod_397_times_600_plus_image_type_times_1500_plus_layer_count_times_4000,
)


# --- F1: xcf_file_size_mod_389_times_650_plus_image_type_times_4000_plus_width_times_height_times_3300 ---

class TestXcfFileSizeMod389Times650PlusImageType4000PlusWidthHeight3300:
    def test_red_returns_118350(self):
        assert xcf_file_size_mod_389_times_650_plus_image_type_times_4000_plus_width_times_height_times_3300(RED) == 118350

    def test_blue_returns_119000(self):
        assert xcf_file_size_mod_389_times_650_plus_image_type_times_4000_plus_width_times_height_times_3300(BLUE) == 119000

    def test_gray_returns_132900(self):
        assert xcf_file_size_mod_389_times_650_plus_image_type_times_4000_plus_width_times_height_times_3300(GRAY) == 132900

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_389_times_650_plus_image_type_times_4000_plus_width_times_height_times_3300(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_389_times_650_plus_image_type_times_4000_plus_width_times_height_times_3300(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_389_times_650_plus_image_type_times_4000_plus_width_times_height_times_3300(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_389_times_650_plus_image_type_times_4000_plus_width_times_height_times_3300(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_389_times_650_plus_image_type_times_4000_plus_width_times_height_times_3300(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_389_times_650_plus_image_type_times_4000_plus_width_times_height_times_3300(GRAY) >
                xcf_file_size_mod_389_times_650_plus_image_type_times_4000_plus_width_times_height_times_3300(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_389_times_650_plus_image_type_times_4000_plus_width_times_height_times_3300(str(RED)) == 118350


# --- F2: xcf_file_size_mod_397_times_600_plus_image_type_times_1500_plus_layer_count_times_4000 ---

class TestXcfFileSizeMod397Times600PlusImageType1500PlusLayerCount4000:
    def test_red_returns_110200(self):
        assert xcf_file_size_mod_397_times_600_plus_image_type_times_1500_plus_layer_count_times_4000(RED) == 110200

    def test_blue_returns_110800(self):
        assert xcf_file_size_mod_397_times_600_plus_image_type_times_1500_plus_layer_count_times_4000(BLUE) == 110800

    def test_gray_returns_112300(self):
        assert xcf_file_size_mod_397_times_600_plus_image_type_times_1500_plus_layer_count_times_4000(GRAY) == 112300

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_397_times_600_plus_image_type_times_1500_plus_layer_count_times_4000(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_397_times_600_plus_image_type_times_1500_plus_layer_count_times_4000(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_397_times_600_plus_image_type_times_1500_plus_layer_count_times_4000(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_397_times_600_plus_image_type_times_1500_plus_layer_count_times_4000(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_397_times_600_plus_image_type_times_1500_plus_layer_count_times_4000(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_397_times_600_plus_image_type_times_1500_plus_layer_count_times_4000(GRAY) >
                xcf_file_size_mod_397_times_600_plus_image_type_times_1500_plus_layer_count_times_4000(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_397_times_600_plus_image_type_times_1500_plus_layer_count_times_4000(str(RED)) == 110200
