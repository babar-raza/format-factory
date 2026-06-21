"""Sprint 393 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_587_times_1025_plus_image_type_times_5500_plus_width_times_height_times_4800,
    xcf_file_size_mod_593_times_975_plus_image_type_times_2250_plus_layer_count_times_5500,
)


# --- F1: xcf_file_size_mod_587_times_1025_plus_image_type_times_5500_plus_width_times_height_times_4800 ---

class TestXcfFileSizeMod587Times1025PlusImageType5500PlusWidthHeight4800:
    def test_red_returns_186225(self):
        assert xcf_file_size_mod_587_times_1025_plus_image_type_times_5500_plus_width_times_height_times_4800(RED) == 186225

    def test_blue_returns_187250(self):
        assert xcf_file_size_mod_587_times_1025_plus_image_type_times_5500_plus_width_times_height_times_4800(BLUE) == 187250

    def test_gray_returns_207150(self):
        assert xcf_file_size_mod_587_times_1025_plus_image_type_times_5500_plus_width_times_height_times_4800(GRAY) == 207150

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_587_times_1025_plus_image_type_times_5500_plus_width_times_height_times_4800(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_587_times_1025_plus_image_type_times_5500_plus_width_times_height_times_4800(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_587_times_1025_plus_image_type_times_5500_plus_width_times_height_times_4800(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_587_times_1025_plus_image_type_times_5500_plus_width_times_height_times_4800(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_587_times_1025_plus_image_type_times_5500_plus_width_times_height_times_4800(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_587_times_1025_plus_image_type_times_5500_plus_width_times_height_times_4800(GRAY) >
                xcf_file_size_mod_587_times_1025_plus_image_type_times_5500_plus_width_times_height_times_4800(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_587_times_1025_plus_image_type_times_5500_plus_width_times_height_times_4800(str(RED)) == 186225


# --- F2: xcf_file_size_mod_593_times_975_plus_image_type_times_2250_plus_layer_count_times_5500 ---

class TestXcfFileSizeMod593Times975PlusImageType2250PlusLayerCount5500:
    def test_red_returns_178075(self):
        assert xcf_file_size_mod_593_times_975_plus_image_type_times_2250_plus_layer_count_times_5500(RED) == 178075

    def test_blue_returns_179050(self):
        assert xcf_file_size_mod_593_times_975_plus_image_type_times_2250_plus_layer_count_times_5500(BLUE) == 179050

    def test_gray_returns_181300(self):
        assert xcf_file_size_mod_593_times_975_plus_image_type_times_2250_plus_layer_count_times_5500(GRAY) == 181300

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_593_times_975_plus_image_type_times_2250_plus_layer_count_times_5500(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_593_times_975_plus_image_type_times_2250_plus_layer_count_times_5500(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_593_times_975_plus_image_type_times_2250_plus_layer_count_times_5500(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_593_times_975_plus_image_type_times_2250_plus_layer_count_times_5500(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_593_times_975_plus_image_type_times_2250_plus_layer_count_times_5500(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_593_times_975_plus_image_type_times_2250_plus_layer_count_times_5500(GRAY) >
                xcf_file_size_mod_593_times_975_plus_image_type_times_2250_plus_layer_count_times_5500(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_593_times_975_plus_image_type_times_2250_plus_layer_count_times_5500(str(RED)) == 178075
