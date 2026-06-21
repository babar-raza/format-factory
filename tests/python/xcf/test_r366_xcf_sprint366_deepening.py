"""Sprint 366 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_461_times_800_plus_image_type_times_4600_plus_width_times_height_times_3900,
    xcf_file_size_mod_463_times_750_plus_image_type_times_1800_plus_layer_count_times_4600,
)


# --- F1: xcf_file_size_mod_461_times_800_plus_image_type_times_4600_plus_width_times_height_times_3900 ---

class TestXcfFileSizeMod461Times800PlusImageType4600PlusWidthHeight3900:
    def test_red_returns_145500(self):
        assert xcf_file_size_mod_461_times_800_plus_image_type_times_4600_plus_width_times_height_times_3900(RED) == 145500

    def test_blue_returns_146300(self):
        assert xcf_file_size_mod_461_times_800_plus_image_type_times_4600_plus_width_times_height_times_3900(BLUE) == 146300

    def test_gray_returns_162600(self):
        assert xcf_file_size_mod_461_times_800_plus_image_type_times_4600_plus_width_times_height_times_3900(GRAY) == 162600

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_461_times_800_plus_image_type_times_4600_plus_width_times_height_times_3900(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_461_times_800_plus_image_type_times_4600_plus_width_times_height_times_3900(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_461_times_800_plus_image_type_times_4600_plus_width_times_height_times_3900(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_461_times_800_plus_image_type_times_4600_plus_width_times_height_times_3900(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_461_times_800_plus_image_type_times_4600_plus_width_times_height_times_3900(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_461_times_800_plus_image_type_times_4600_plus_width_times_height_times_3900(GRAY) >
                xcf_file_size_mod_461_times_800_plus_image_type_times_4600_plus_width_times_height_times_3900(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_461_times_800_plus_image_type_times_4600_plus_width_times_height_times_3900(str(RED)) == 145500


# --- F2: xcf_file_size_mod_463_times_750_plus_image_type_times_1800_plus_layer_count_times_4600 ---

class TestXcfFileSizeMod463Times750PlusImageType1800PlusLayerCount4600:
    def test_red_returns_137350(self):
        assert xcf_file_size_mod_463_times_750_plus_image_type_times_1800_plus_layer_count_times_4600(RED) == 137350

    def test_blue_returns_138100(self):
        assert xcf_file_size_mod_463_times_750_plus_image_type_times_1800_plus_layer_count_times_4600(BLUE) == 138100

    def test_gray_returns_139900(self):
        assert xcf_file_size_mod_463_times_750_plus_image_type_times_1800_plus_layer_count_times_4600(GRAY) == 139900

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_463_times_750_plus_image_type_times_1800_plus_layer_count_times_4600(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_463_times_750_plus_image_type_times_1800_plus_layer_count_times_4600(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_463_times_750_plus_image_type_times_1800_plus_layer_count_times_4600(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_463_times_750_plus_image_type_times_1800_plus_layer_count_times_4600(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_463_times_750_plus_image_type_times_1800_plus_layer_count_times_4600(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_463_times_750_plus_image_type_times_1800_plus_layer_count_times_4600(GRAY) >
                xcf_file_size_mod_463_times_750_plus_image_type_times_1800_plus_layer_count_times_4600(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_463_times_750_plus_image_type_times_1800_plus_layer_count_times_4600(str(RED)) == 137350
