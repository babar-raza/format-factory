"""Sprint 384 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_547_times_950_plus_image_type_times_5200_plus_width_times_height_times_4500,
    xcf_file_size_mod_557_times_900_plus_image_type_times_2100_plus_layer_count_times_5200,
)


# --- F1: xcf_file_size_mod_547_times_950_plus_image_type_times_5200_plus_width_times_height_times_4500 ---

class TestXcfFileSizeMod547Times950PlusImageType5200PlusWidthHeight4500:
    def test_red_returns_172650(self):
        assert xcf_file_size_mod_547_times_950_plus_image_type_times_5200_plus_width_times_height_times_4500(RED) == 172650

    def test_blue_returns_173600(self):
        assert xcf_file_size_mod_547_times_950_plus_image_type_times_5200_plus_width_times_height_times_4500(BLUE) == 173600

    def test_gray_returns_192300(self):
        assert xcf_file_size_mod_547_times_950_plus_image_type_times_5200_plus_width_times_height_times_4500(GRAY) == 192300

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_547_times_950_plus_image_type_times_5200_plus_width_times_height_times_4500(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_547_times_950_plus_image_type_times_5200_plus_width_times_height_times_4500(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_547_times_950_plus_image_type_times_5200_plus_width_times_height_times_4500(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_547_times_950_plus_image_type_times_5200_plus_width_times_height_times_4500(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_547_times_950_plus_image_type_times_5200_plus_width_times_height_times_4500(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_547_times_950_plus_image_type_times_5200_plus_width_times_height_times_4500(GRAY) >
                xcf_file_size_mod_547_times_950_plus_image_type_times_5200_plus_width_times_height_times_4500(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_547_times_950_plus_image_type_times_5200_plus_width_times_height_times_4500(str(RED)) == 172650


# --- F2: xcf_file_size_mod_557_times_900_plus_image_type_times_2100_plus_layer_count_times_5200 ---

class TestXcfFileSizeMod557Times900PlusImageType2100PlusLayerCount5200:
    def test_red_returns_164500(self):
        assert xcf_file_size_mod_557_times_900_plus_image_type_times_2100_plus_layer_count_times_5200(RED) == 164500

    def test_blue_returns_165400(self):
        assert xcf_file_size_mod_557_times_900_plus_image_type_times_2100_plus_layer_count_times_5200(BLUE) == 165400

    def test_gray_returns_167500(self):
        assert xcf_file_size_mod_557_times_900_plus_image_type_times_2100_plus_layer_count_times_5200(GRAY) == 167500

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_557_times_900_plus_image_type_times_2100_plus_layer_count_times_5200(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_557_times_900_plus_image_type_times_2100_plus_layer_count_times_5200(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_557_times_900_plus_image_type_times_2100_plus_layer_count_times_5200(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_557_times_900_plus_image_type_times_2100_plus_layer_count_times_5200(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_557_times_900_plus_image_type_times_2100_plus_layer_count_times_5200(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_557_times_900_plus_image_type_times_2100_plus_layer_count_times_5200(GRAY) >
                xcf_file_size_mod_557_times_900_plus_image_type_times_2100_plus_layer_count_times_5200(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_557_times_900_plus_image_type_times_2100_plus_layer_count_times_5200(str(RED)) == 164500
