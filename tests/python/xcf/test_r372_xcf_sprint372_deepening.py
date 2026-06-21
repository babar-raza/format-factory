"""Sprint 372 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_487_times_850_plus_image_type_times_4800_plus_width_times_height_times_4100,
    xcf_file_size_mod_491_times_800_plus_image_type_times_1900_plus_layer_count_times_4800,
)


# --- F1: xcf_file_size_mod_487_times_850_plus_image_type_times_4800_plus_width_times_height_times_4100 ---

class TestXcfFileSizeMod487Times850PlusImageType4800PlusWidthHeight4100:
    def test_red_returns_154550(self):
        assert xcf_file_size_mod_487_times_850_plus_image_type_times_4800_plus_width_times_height_times_4100(RED) == 154550

    def test_blue_returns_155400(self):
        assert xcf_file_size_mod_487_times_850_plus_image_type_times_4800_plus_width_times_height_times_4100(BLUE) == 155400

    def test_gray_returns_172500(self):
        assert xcf_file_size_mod_487_times_850_plus_image_type_times_4800_plus_width_times_height_times_4100(GRAY) == 172500

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_487_times_850_plus_image_type_times_4800_plus_width_times_height_times_4100(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_487_times_850_plus_image_type_times_4800_plus_width_times_height_times_4100(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_487_times_850_plus_image_type_times_4800_plus_width_times_height_times_4100(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_487_times_850_plus_image_type_times_4800_plus_width_times_height_times_4100(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_487_times_850_plus_image_type_times_4800_plus_width_times_height_times_4100(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_487_times_850_plus_image_type_times_4800_plus_width_times_height_times_4100(GRAY) >
                xcf_file_size_mod_487_times_850_plus_image_type_times_4800_plus_width_times_height_times_4100(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_487_times_850_plus_image_type_times_4800_plus_width_times_height_times_4100(str(RED)) == 154550


# --- F2: xcf_file_size_mod_491_times_800_plus_image_type_times_1900_plus_layer_count_times_4800 ---

class TestXcfFileSizeMod491Times800PlusImageType1900PlusLayerCount4800:
    def test_red_returns_146400(self):
        assert xcf_file_size_mod_491_times_800_plus_image_type_times_1900_plus_layer_count_times_4800(RED) == 146400

    def test_blue_returns_147200(self):
        assert xcf_file_size_mod_491_times_800_plus_image_type_times_1900_plus_layer_count_times_4800(BLUE) == 147200

    def test_gray_returns_149100(self):
        assert xcf_file_size_mod_491_times_800_plus_image_type_times_1900_plus_layer_count_times_4800(GRAY) == 149100

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_491_times_800_plus_image_type_times_1900_plus_layer_count_times_4800(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_491_times_800_plus_image_type_times_1900_plus_layer_count_times_4800(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_491_times_800_plus_image_type_times_1900_plus_layer_count_times_4800(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_491_times_800_plus_image_type_times_1900_plus_layer_count_times_4800(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_491_times_800_plus_image_type_times_1900_plus_layer_count_times_4800(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_491_times_800_plus_image_type_times_1900_plus_layer_count_times_4800(GRAY) >
                xcf_file_size_mod_491_times_800_plus_image_type_times_1900_plus_layer_count_times_4800(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_491_times_800_plus_image_type_times_1900_plus_layer_count_times_4800(str(RED)) == 146400
