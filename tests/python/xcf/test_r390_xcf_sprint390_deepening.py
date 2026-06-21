"""Sprint 390 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_571_times_1000_plus_image_type_times_5400_plus_width_times_height_times_4700,
    xcf_file_size_mod_577_times_950_plus_image_type_times_2200_plus_layer_count_times_5400,
)


# --- F1: xcf_file_size_mod_571_times_1000_plus_image_type_times_5400_plus_width_times_height_times_4700 ---

class TestXcfFileSizeMod571Times1000PlusImageType5400PlusWidthHeight4700:
    def test_red_returns_181700(self):
        assert xcf_file_size_mod_571_times_1000_plus_image_type_times_5400_plus_width_times_height_times_4700(RED) == 181700

    def test_blue_returns_182700(self):
        assert xcf_file_size_mod_571_times_1000_plus_image_type_times_5400_plus_width_times_height_times_4700(BLUE) == 182700

    def test_gray_returns_202200(self):
        assert xcf_file_size_mod_571_times_1000_plus_image_type_times_5400_plus_width_times_height_times_4700(GRAY) == 202200

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_571_times_1000_plus_image_type_times_5400_plus_width_times_height_times_4700(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_571_times_1000_plus_image_type_times_5400_plus_width_times_height_times_4700(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_571_times_1000_plus_image_type_times_5400_plus_width_times_height_times_4700(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_571_times_1000_plus_image_type_times_5400_plus_width_times_height_times_4700(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_571_times_1000_plus_image_type_times_5400_plus_width_times_height_times_4700(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_571_times_1000_plus_image_type_times_5400_plus_width_times_height_times_4700(GRAY) >
                xcf_file_size_mod_571_times_1000_plus_image_type_times_5400_plus_width_times_height_times_4700(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_571_times_1000_plus_image_type_times_5400_plus_width_times_height_times_4700(str(RED)) == 181700


# --- F2: xcf_file_size_mod_577_times_950_plus_image_type_times_2200_plus_layer_count_times_5400 ---

class TestXcfFileSizeMod577Times950PlusImageType2200PlusLayerCount5400:
    def test_red_returns_173550(self):
        assert xcf_file_size_mod_577_times_950_plus_image_type_times_2200_plus_layer_count_times_5400(RED) == 173550

    def test_blue_returns_174500(self):
        assert xcf_file_size_mod_577_times_950_plus_image_type_times_2200_plus_layer_count_times_5400(BLUE) == 174500

    def test_gray_returns_176700(self):
        assert xcf_file_size_mod_577_times_950_plus_image_type_times_2200_plus_layer_count_times_5400(GRAY) == 176700

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_577_times_950_plus_image_type_times_2200_plus_layer_count_times_5400(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_577_times_950_plus_image_type_times_2200_plus_layer_count_times_5400(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_577_times_950_plus_image_type_times_2200_plus_layer_count_times_5400(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_577_times_950_plus_image_type_times_2200_plus_layer_count_times_5400(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_577_times_950_plus_image_type_times_2200_plus_layer_count_times_5400(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_577_times_950_plus_image_type_times_2200_plus_layer_count_times_5400(GRAY) >
                xcf_file_size_mod_577_times_950_plus_image_type_times_2200_plus_layer_count_times_5400(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_577_times_950_plus_image_type_times_2200_plus_layer_count_times_5400(str(RED)) == 173550
