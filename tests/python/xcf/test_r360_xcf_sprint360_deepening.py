"""Sprint 360 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_439_times_750_plus_image_type_times_4400_plus_width_times_height_times_3700,
    xcf_file_size_mod_443_times_700_plus_image_type_times_1700_plus_layer_count_times_4400,
)


# --- F1: xcf_file_size_mod_439_times_750_plus_image_type_times_4400_plus_width_times_height_times_3700 ---

class TestXcfFileSizeMod439Times750PlusImageType4400PlusWidthHeight3700:
    def test_red_returns_136450(self):
        assert xcf_file_size_mod_439_times_750_plus_image_type_times_4400_plus_width_times_height_times_3700(RED) == 136450

    def test_blue_returns_137200(self):
        assert xcf_file_size_mod_439_times_750_plus_image_type_times_4400_plus_width_times_height_times_3700(BLUE) == 137200

    def test_gray_returns_152700(self):
        assert xcf_file_size_mod_439_times_750_plus_image_type_times_4400_plus_width_times_height_times_3700(GRAY) == 152700

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_439_times_750_plus_image_type_times_4400_plus_width_times_height_times_3700(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_439_times_750_plus_image_type_times_4400_plus_width_times_height_times_3700(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_439_times_750_plus_image_type_times_4400_plus_width_times_height_times_3700(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_439_times_750_plus_image_type_times_4400_plus_width_times_height_times_3700(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_439_times_750_plus_image_type_times_4400_plus_width_times_height_times_3700(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_439_times_750_plus_image_type_times_4400_plus_width_times_height_times_3700(GRAY) >
                xcf_file_size_mod_439_times_750_plus_image_type_times_4400_plus_width_times_height_times_3700(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_439_times_750_plus_image_type_times_4400_plus_width_times_height_times_3700(str(RED)) == 136450


# --- F2: xcf_file_size_mod_443_times_700_plus_image_type_times_1700_plus_layer_count_times_4400 ---

class TestXcfFileSizeMod443Times700PlusImageType1700PlusLayerCount4400:
    def test_red_returns_128300(self):
        assert xcf_file_size_mod_443_times_700_plus_image_type_times_1700_plus_layer_count_times_4400(RED) == 128300

    def test_blue_returns_129000(self):
        assert xcf_file_size_mod_443_times_700_plus_image_type_times_1700_plus_layer_count_times_4400(BLUE) == 129000

    def test_gray_returns_130700(self):
        assert xcf_file_size_mod_443_times_700_plus_image_type_times_1700_plus_layer_count_times_4400(GRAY) == 130700

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_443_times_700_plus_image_type_times_1700_plus_layer_count_times_4400(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_443_times_700_plus_image_type_times_1700_plus_layer_count_times_4400(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_443_times_700_plus_image_type_times_1700_plus_layer_count_times_4400(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_443_times_700_plus_image_type_times_1700_plus_layer_count_times_4400(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_443_times_700_plus_image_type_times_1700_plus_layer_count_times_4400(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_443_times_700_plus_image_type_times_1700_plus_layer_count_times_4400(GRAY) >
                xcf_file_size_mod_443_times_700_plus_image_type_times_1700_plus_layer_count_times_4400(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_443_times_700_plus_image_type_times_1700_plus_layer_count_times_4400(str(RED)) == 128300
