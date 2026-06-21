"""Sprint 378 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_509_times_900_plus_image_type_times_5000_plus_width_times_height_times_4300,
    xcf_file_size_mod_521_times_850_plus_image_type_times_2000_plus_layer_count_times_5000,
)


# --- F1: xcf_file_size_mod_509_times_900_plus_image_type_times_5000_plus_width_times_height_times_4300 ---

class TestXcfFileSizeMod509Times900PlusImageType5000PlusWidthHeight4300:
    def test_red_returns_163600(self):
        assert xcf_file_size_mod_509_times_900_plus_image_type_times_5000_plus_width_times_height_times_4300(RED) == 163600

    def test_blue_returns_164500(self):
        assert xcf_file_size_mod_509_times_900_plus_image_type_times_5000_plus_width_times_height_times_4300(BLUE) == 164500

    def test_gray_returns_182400(self):
        assert xcf_file_size_mod_509_times_900_plus_image_type_times_5000_plus_width_times_height_times_4300(GRAY) == 182400

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_509_times_900_plus_image_type_times_5000_plus_width_times_height_times_4300(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_509_times_900_plus_image_type_times_5000_plus_width_times_height_times_4300(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_509_times_900_plus_image_type_times_5000_plus_width_times_height_times_4300(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_509_times_900_plus_image_type_times_5000_plus_width_times_height_times_4300(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_509_times_900_plus_image_type_times_5000_plus_width_times_height_times_4300(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_509_times_900_plus_image_type_times_5000_plus_width_times_height_times_4300(GRAY) >
                xcf_file_size_mod_509_times_900_plus_image_type_times_5000_plus_width_times_height_times_4300(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_509_times_900_plus_image_type_times_5000_plus_width_times_height_times_4300(str(RED)) == 163600


# --- F2: xcf_file_size_mod_521_times_850_plus_image_type_times_2000_plus_layer_count_times_5000 ---

class TestXcfFileSizeMod521Times850PlusImageType2000PlusLayerCount5000:
    def test_red_returns_155450(self):
        assert xcf_file_size_mod_521_times_850_plus_image_type_times_2000_plus_layer_count_times_5000(RED) == 155450

    def test_blue_returns_156300(self):
        assert xcf_file_size_mod_521_times_850_plus_image_type_times_2000_plus_layer_count_times_5000(BLUE) == 156300

    def test_gray_returns_158300(self):
        assert xcf_file_size_mod_521_times_850_plus_image_type_times_2000_plus_layer_count_times_5000(GRAY) == 158300

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_521_times_850_plus_image_type_times_2000_plus_layer_count_times_5000(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_521_times_850_plus_image_type_times_2000_plus_layer_count_times_5000(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_521_times_850_plus_image_type_times_2000_plus_layer_count_times_5000(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_521_times_850_plus_image_type_times_2000_plus_layer_count_times_5000(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_521_times_850_plus_image_type_times_2000_plus_layer_count_times_5000(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_521_times_850_plus_image_type_times_2000_plus_layer_count_times_5000(GRAY) >
                xcf_file_size_mod_521_times_850_plus_image_type_times_2000_plus_layer_count_times_5000(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_521_times_850_plus_image_type_times_2000_plus_layer_count_times_5000(str(RED)) == 155450
