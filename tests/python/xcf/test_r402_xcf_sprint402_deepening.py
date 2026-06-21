"""Sprint 402 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_617_times_1100_plus_image_type_times_5800_plus_width_times_height_times_5100,
    xcf_file_size_mod_619_times_1050_plus_image_type_times_2400_plus_layer_count_times_5800,
)


# --- F1: xcf_file_size_mod_617_times_1100_plus_image_type_times_5800_plus_width_times_height_times_5100 ---

class TestXcfFileSizeMod617Times1100PlusImageType5800PlusWidthHeight5100:
    def test_red_returns_199800(self):
        assert xcf_file_size_mod_617_times_1100_plus_image_type_times_5800_plus_width_times_height_times_5100(RED) == 199800

    def test_blue_returns_200900(self):
        assert xcf_file_size_mod_617_times_1100_plus_image_type_times_5800_plus_width_times_height_times_5100(BLUE) == 200900

    def test_gray_returns_222000(self):
        assert xcf_file_size_mod_617_times_1100_plus_image_type_times_5800_plus_width_times_height_times_5100(GRAY) == 222000

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_617_times_1100_plus_image_type_times_5800_plus_width_times_height_times_5100(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_617_times_1100_plus_image_type_times_5800_plus_width_times_height_times_5100(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_617_times_1100_plus_image_type_times_5800_plus_width_times_height_times_5100(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_617_times_1100_plus_image_type_times_5800_plus_width_times_height_times_5100(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_617_times_1100_plus_image_type_times_5800_plus_width_times_height_times_5100(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_617_times_1100_plus_image_type_times_5800_plus_width_times_height_times_5100(GRAY) >
                xcf_file_size_mod_617_times_1100_plus_image_type_times_5800_plus_width_times_height_times_5100(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_617_times_1100_plus_image_type_times_5800_plus_width_times_height_times_5100(str(RED)) == 199800


# --- F2: xcf_file_size_mod_619_times_1050_plus_image_type_times_2400_plus_layer_count_times_5800 ---

class TestXcfFileSizeMod619Times1050PlusImageType2400PlusLayerCount5800:
    def test_red_returns_191650(self):
        assert xcf_file_size_mod_619_times_1050_plus_image_type_times_2400_plus_layer_count_times_5800(RED) == 191650

    def test_blue_returns_192700(self):
        assert xcf_file_size_mod_619_times_1050_plus_image_type_times_2400_plus_layer_count_times_5800(BLUE) == 192700

    def test_gray_returns_195100(self):
        assert xcf_file_size_mod_619_times_1050_plus_image_type_times_2400_plus_layer_count_times_5800(GRAY) == 195100

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_619_times_1050_plus_image_type_times_2400_plus_layer_count_times_5800(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_619_times_1050_plus_image_type_times_2400_plus_layer_count_times_5800(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_619_times_1050_plus_image_type_times_2400_plus_layer_count_times_5800(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_619_times_1050_plus_image_type_times_2400_plus_layer_count_times_5800(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_619_times_1050_plus_image_type_times_2400_plus_layer_count_times_5800(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_619_times_1050_plus_image_type_times_2400_plus_layer_count_times_5800(GRAY) >
                xcf_file_size_mod_619_times_1050_plus_image_type_times_2400_plus_layer_count_times_5800(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_619_times_1050_plus_image_type_times_2400_plus_layer_count_times_5800(str(RED)) == 191650
