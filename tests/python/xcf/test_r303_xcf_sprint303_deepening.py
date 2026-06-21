"""Sprint 303 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_179_times_275_plus_image_type_times_2500_plus_width_times_height_times_1800,
    xcf_file_size_mod_181_times_225_plus_image_type_times_750_plus_layer_count_times_2500,
)


# --- F1: xcf_file_size_mod_179_times_275_plus_image_type_times_2500_plus_width_times_height_times_1800 ---

class TestXcfFileSizeMod179Times275PlusImageType2500PlusWidthTimesHeight1800:
    def test_red_returns_50475(self):
        assert xcf_file_size_mod_179_times_275_plus_image_type_times_2500_plus_width_times_height_times_1800(RED) == 50475

    def test_blue_returns_50750(self):
        assert xcf_file_size_mod_179_times_275_plus_image_type_times_2500_plus_width_times_height_times_1800(BLUE) == 50750

    def test_gray_returns_58650(self):
        assert xcf_file_size_mod_179_times_275_plus_image_type_times_2500_plus_width_times_height_times_1800(GRAY) == 58650

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_179_times_275_plus_image_type_times_2500_plus_width_times_height_times_1800(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_179_times_275_plus_image_type_times_2500_plus_width_times_height_times_1800(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_179_times_275_plus_image_type_times_2500_plus_width_times_height_times_1800(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_179_times_275_plus_image_type_times_2500_plus_width_times_height_times_1800(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_179_times_275_plus_image_type_times_2500_plus_width_times_height_times_1800(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_179_times_275_plus_image_type_times_2500_plus_width_times_height_times_1800(GRAY) >
                xcf_file_size_mod_179_times_275_plus_image_type_times_2500_plus_width_times_height_times_1800(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_179_times_275_plus_image_type_times_2500_plus_width_times_height_times_1800(str(RED)) == 50475


# --- F2: xcf_file_size_mod_181_times_225_plus_image_type_times_750_plus_layer_count_times_2500 ---

class TestXcfFileSizeMod181Times225PlusImageType750PlusLayerCount2500:
    def test_red_returns_42325(self):
        assert xcf_file_size_mod_181_times_225_plus_image_type_times_750_plus_layer_count_times_2500(RED) == 42325

    def test_blue_returns_42550(self):
        assert xcf_file_size_mod_181_times_225_plus_image_type_times_750_plus_layer_count_times_2500(BLUE) == 42550

    def test_gray_returns_43300(self):
        assert xcf_file_size_mod_181_times_225_plus_image_type_times_750_plus_layer_count_times_2500(GRAY) == 43300

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_181_times_225_plus_image_type_times_750_plus_layer_count_times_2500(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_181_times_225_plus_image_type_times_750_plus_layer_count_times_2500(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_181_times_225_plus_image_type_times_750_plus_layer_count_times_2500(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_181_times_225_plus_image_type_times_750_plus_layer_count_times_2500(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_181_times_225_plus_image_type_times_750_plus_layer_count_times_2500(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_181_times_225_plus_image_type_times_750_plus_layer_count_times_2500(GRAY) >
                xcf_file_size_mod_181_times_225_plus_image_type_times_750_plus_layer_count_times_2500(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_181_times_225_plus_image_type_times_750_plus_layer_count_times_2500(str(RED)) == 42325
