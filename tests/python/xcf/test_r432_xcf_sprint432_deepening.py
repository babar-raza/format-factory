"""Sprint 432 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_751_times_1350_plus_image_type_times_6800_plus_width_times_height_times_6100,
    xcf_file_size_mod_757_times_1300_plus_image_type_times_2900_plus_layer_count_times_6800,
)


# --- F1: xcf_file_size_mod_751_times_1350_plus_image_type_times_6800_plus_width_times_height_times_6100 ---

class TestXcfFileSizeMod751Times1350PlusImageType6800PlusWidthHeight6100:
    def test_red_returns_245050(self):
        assert xcf_file_size_mod_751_times_1350_plus_image_type_times_6800_plus_width_times_height_times_6100(RED) == 245050

    def test_blue_returns_246400(self):
        assert xcf_file_size_mod_751_times_1350_plus_image_type_times_6800_plus_width_times_height_times_6100(BLUE) == 246400

    def test_gray_returns_271500(self):
        assert xcf_file_size_mod_751_times_1350_plus_image_type_times_6800_plus_width_times_height_times_6100(GRAY) == 271500

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_751_times_1350_plus_image_type_times_6800_plus_width_times_height_times_6100(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_751_times_1350_plus_image_type_times_6800_plus_width_times_height_times_6100(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_751_times_1350_plus_image_type_times_6800_plus_width_times_height_times_6100(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_751_times_1350_plus_image_type_times_6800_plus_width_times_height_times_6100(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_751_times_1350_plus_image_type_times_6800_plus_width_times_height_times_6100(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_751_times_1350_plus_image_type_times_6800_plus_width_times_height_times_6100(GRAY) >
                xcf_file_size_mod_751_times_1350_plus_image_type_times_6800_plus_width_times_height_times_6100(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_751_times_1350_plus_image_type_times_6800_plus_width_times_height_times_6100(str(RED)) == 245050


# --- F2: xcf_file_size_mod_757_times_1300_plus_image_type_times_2900_plus_layer_count_times_6800 ---

class TestXcfFileSizeMod757Times1300PlusImageType2900PlusLayerCount6800:
    def test_red_returns_236900(self):
        assert xcf_file_size_mod_757_times_1300_plus_image_type_times_2900_plus_layer_count_times_6800(RED) == 236900

    def test_blue_returns_238200(self):
        assert xcf_file_size_mod_757_times_1300_plus_image_type_times_2900_plus_layer_count_times_6800(BLUE) == 238200

    def test_gray_returns_241100(self):
        assert xcf_file_size_mod_757_times_1300_plus_image_type_times_2900_plus_layer_count_times_6800(GRAY) == 241100

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_757_times_1300_plus_image_type_times_2900_plus_layer_count_times_6800(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_757_times_1300_plus_image_type_times_2900_plus_layer_count_times_6800(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_757_times_1300_plus_image_type_times_2900_plus_layer_count_times_6800(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_757_times_1300_plus_image_type_times_2900_plus_layer_count_times_6800(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_757_times_1300_plus_image_type_times_2900_plus_layer_count_times_6800(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_757_times_1300_plus_image_type_times_2900_plus_layer_count_times_6800(GRAY) >
                xcf_file_size_mod_757_times_1300_plus_image_type_times_2900_plus_layer_count_times_6800(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_757_times_1300_plus_image_type_times_2900_plus_layer_count_times_6800(str(RED)) == 236900
