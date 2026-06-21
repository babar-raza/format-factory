"""Sprint 291 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_127_times_250_plus_image_type_times_2000_plus_width_times_height_times_1300,
    xcf_file_size_mod_131_times_125_plus_image_type_times_500_plus_layer_count_times_2000,
)


# --- F1: xcf_file_size_mod_127_times_250_plus_image_type_times_2000_plus_width_times_height_times_1300 ---

class TestXcfFileSizeMod127Times250PlusImageType2000PlusWidthTimesHeight1300:
    def test_red_returns_13800(self):
        assert xcf_file_size_mod_127_times_250_plus_image_type_times_2000_plus_width_times_height_times_1300(RED) == 13800

    def test_blue_returns_14050(self):
        assert xcf_file_size_mod_127_times_250_plus_image_type_times_2000_plus_width_times_height_times_1300(BLUE) == 14050

    def test_gray_returns_19950(self):
        assert xcf_file_size_mod_127_times_250_plus_image_type_times_2000_plus_width_times_height_times_1300(GRAY) == 19950

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_127_times_250_plus_image_type_times_2000_plus_width_times_height_times_1300(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_127_times_250_plus_image_type_times_2000_plus_width_times_height_times_1300(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_127_times_250_plus_image_type_times_2000_plus_width_times_height_times_1300(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_127_times_250_plus_image_type_times_2000_plus_width_times_height_times_1300(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_127_times_250_plus_image_type_times_2000_plus_width_times_height_times_1300(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_127_times_250_plus_image_type_times_2000_plus_width_times_height_times_1300(GRAY) >
                xcf_file_size_mod_127_times_250_plus_image_type_times_2000_plus_width_times_height_times_1300(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_127_times_250_plus_image_type_times_2000_plus_width_times_height_times_1300(str(RED)) == 13800


# --- F2: xcf_file_size_mod_131_times_125_plus_image_type_times_500_plus_layer_count_times_2000 ---

class TestXcfFileSizeMod131Times125PlusImageType500PlusLayerCount2000:
    def test_red_returns_7750(self):
        assert xcf_file_size_mod_131_times_125_plus_image_type_times_500_plus_layer_count_times_2000(RED) == 7750

    def test_blue_returns_7875(self):
        assert xcf_file_size_mod_131_times_125_plus_image_type_times_500_plus_layer_count_times_2000(BLUE) == 7875

    def test_gray_returns_8375(self):
        assert xcf_file_size_mod_131_times_125_plus_image_type_times_500_plus_layer_count_times_2000(GRAY) == 8375

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_131_times_125_plus_image_type_times_500_plus_layer_count_times_2000(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_131_times_125_plus_image_type_times_500_plus_layer_count_times_2000(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_131_times_125_plus_image_type_times_500_plus_layer_count_times_2000(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_131_times_125_plus_image_type_times_500_plus_layer_count_times_2000(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_131_times_125_plus_image_type_times_500_plus_layer_count_times_2000(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_131_times_125_plus_image_type_times_500_plus_layer_count_times_2000(GRAY) >
                xcf_file_size_mod_131_times_125_plus_image_type_times_500_plus_layer_count_times_2000(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_131_times_125_plus_image_type_times_500_plus_layer_count_times_2000(str(RED)) == 7750
