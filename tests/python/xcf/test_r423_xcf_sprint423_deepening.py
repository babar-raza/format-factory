"""Sprint 423 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_709_times_1275_plus_image_type_times_6500_plus_width_times_height_times_5800,
    xcf_file_size_mod_719_times_1225_plus_image_type_times_2750_plus_layer_count_times_6500,
)


# --- F1: xcf_file_size_mod_709_times_1275_plus_image_type_times_6500_plus_width_times_height_times_5800 ---

class TestXcfFileSizeMod709Times1275PlusImageType6500PlusWidthHeight5800:
    def test_red_returns_231475(self):
        assert xcf_file_size_mod_709_times_1275_plus_image_type_times_6500_plus_width_times_height_times_5800(RED) == 231475

    def test_blue_returns_232750(self):
        assert xcf_file_size_mod_709_times_1275_plus_image_type_times_6500_plus_width_times_height_times_5800(BLUE) == 232750

    def test_gray_returns_256650(self):
        assert xcf_file_size_mod_709_times_1275_plus_image_type_times_6500_plus_width_times_height_times_5800(GRAY) == 256650

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_709_times_1275_plus_image_type_times_6500_plus_width_times_height_times_5800(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_709_times_1275_plus_image_type_times_6500_plus_width_times_height_times_5800(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_709_times_1275_plus_image_type_times_6500_plus_width_times_height_times_5800(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_709_times_1275_plus_image_type_times_6500_plus_width_times_height_times_5800(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_709_times_1275_plus_image_type_times_6500_plus_width_times_height_times_5800(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_709_times_1275_plus_image_type_times_6500_plus_width_times_height_times_5800(GRAY) >
                xcf_file_size_mod_709_times_1275_plus_image_type_times_6500_plus_width_times_height_times_5800(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_709_times_1275_plus_image_type_times_6500_plus_width_times_height_times_5800(str(RED)) == 231475


# --- F2: xcf_file_size_mod_719_times_1225_plus_image_type_times_2750_plus_layer_count_times_6500 ---

class TestXcfFileSizeMod719Times1225PlusImageType2750PlusLayerCount6500:
    def test_red_returns_223325(self):
        assert xcf_file_size_mod_719_times_1225_plus_image_type_times_2750_plus_layer_count_times_6500(RED) == 223325

    def test_blue_returns_224550(self):
        assert xcf_file_size_mod_719_times_1225_plus_image_type_times_2750_plus_layer_count_times_6500(BLUE) == 224550

    def test_gray_returns_227300(self):
        assert xcf_file_size_mod_719_times_1225_plus_image_type_times_2750_plus_layer_count_times_6500(GRAY) == 227300

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_719_times_1225_plus_image_type_times_2750_plus_layer_count_times_6500(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_719_times_1225_plus_image_type_times_2750_plus_layer_count_times_6500(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_719_times_1225_plus_image_type_times_2750_plus_layer_count_times_6500(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_719_times_1225_plus_image_type_times_2750_plus_layer_count_times_6500(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_719_times_1225_plus_image_type_times_2750_plus_layer_count_times_6500(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_719_times_1225_plus_image_type_times_2750_plus_layer_count_times_6500(GRAY) >
                xcf_file_size_mod_719_times_1225_plus_image_type_times_2750_plus_layer_count_times_6500(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_719_times_1225_plus_image_type_times_2750_plus_layer_count_times_6500(str(RED)) == 223325
