"""Sprint 396 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_599_times_1050_plus_image_type_times_5600_plus_width_times_height_times_4900,
    xcf_file_size_mod_601_times_1000_plus_image_type_times_2300_plus_layer_count_times_5600,
)


# --- F1: xcf_file_size_mod_599_times_1050_plus_image_type_times_5600_plus_width_times_height_times_4900 ---

class TestXcfFileSizeMod599Times1050PlusImageType5600PlusWidthHeight4900:
    def test_red_returns_190750(self):
        assert xcf_file_size_mod_599_times_1050_plus_image_type_times_5600_plus_width_times_height_times_4900(RED) == 190750

    def test_blue_returns_191800(self):
        assert xcf_file_size_mod_599_times_1050_plus_image_type_times_5600_plus_width_times_height_times_4900(BLUE) == 191800

    def test_gray_returns_212100(self):
        assert xcf_file_size_mod_599_times_1050_plus_image_type_times_5600_plus_width_times_height_times_4900(GRAY) == 212100

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_599_times_1050_plus_image_type_times_5600_plus_width_times_height_times_4900(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_599_times_1050_plus_image_type_times_5600_plus_width_times_height_times_4900(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_599_times_1050_plus_image_type_times_5600_plus_width_times_height_times_4900(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_599_times_1050_plus_image_type_times_5600_plus_width_times_height_times_4900(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_599_times_1050_plus_image_type_times_5600_plus_width_times_height_times_4900(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_599_times_1050_plus_image_type_times_5600_plus_width_times_height_times_4900(GRAY) >
                xcf_file_size_mod_599_times_1050_plus_image_type_times_5600_plus_width_times_height_times_4900(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_599_times_1050_plus_image_type_times_5600_plus_width_times_height_times_4900(str(RED)) == 190750


# --- F2: xcf_file_size_mod_601_times_1000_plus_image_type_times_2300_plus_layer_count_times_5600 ---

class TestXcfFileSizeMod601Times1000PlusImageType2300PlusLayerCount5600:
    def test_red_returns_182600(self):
        assert xcf_file_size_mod_601_times_1000_plus_image_type_times_2300_plus_layer_count_times_5600(RED) == 182600

    def test_blue_returns_183600(self):
        assert xcf_file_size_mod_601_times_1000_plus_image_type_times_2300_plus_layer_count_times_5600(BLUE) == 183600

    def test_gray_returns_185900(self):
        assert xcf_file_size_mod_601_times_1000_plus_image_type_times_2300_plus_layer_count_times_5600(GRAY) == 185900

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_601_times_1000_plus_image_type_times_2300_plus_layer_count_times_5600(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_601_times_1000_plus_image_type_times_2300_plus_layer_count_times_5600(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_601_times_1000_plus_image_type_times_2300_plus_layer_count_times_5600(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_601_times_1000_plus_image_type_times_2300_plus_layer_count_times_5600(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_601_times_1000_plus_image_type_times_2300_plus_layer_count_times_5600(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_601_times_1000_plus_image_type_times_2300_plus_layer_count_times_5600(GRAY) >
                xcf_file_size_mod_601_times_1000_plus_image_type_times_2300_plus_layer_count_times_5600(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_601_times_1000_plus_image_type_times_2300_plus_layer_count_times_5600(str(RED)) == 182600
