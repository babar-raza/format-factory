"""Sprint 429 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_739_times_1325_plus_image_type_times_6700_plus_width_times_height_times_6000,
    xcf_file_size_mod_743_times_1275_plus_image_type_times_2850_plus_layer_count_times_6700,
)


# --- F1: xcf_file_size_mod_739_times_1325_plus_image_type_times_6700_plus_width_times_height_times_6000 ---

class TestXcfFileSizeMod739Times1325PlusImageType6700PlusWidthHeight6000:
    def test_red_returns_240525(self):
        assert xcf_file_size_mod_739_times_1325_plus_image_type_times_6700_plus_width_times_height_times_6000(RED) == 240525

    def test_blue_returns_241850(self):
        assert xcf_file_size_mod_739_times_1325_plus_image_type_times_6700_plus_width_times_height_times_6000(BLUE) == 241850

    def test_gray_returns_266550(self):
        assert xcf_file_size_mod_739_times_1325_plus_image_type_times_6700_plus_width_times_height_times_6000(GRAY) == 266550

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_739_times_1325_plus_image_type_times_6700_plus_width_times_height_times_6000(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_739_times_1325_plus_image_type_times_6700_plus_width_times_height_times_6000(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_739_times_1325_plus_image_type_times_6700_plus_width_times_height_times_6000(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_739_times_1325_plus_image_type_times_6700_plus_width_times_height_times_6000(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_739_times_1325_plus_image_type_times_6700_plus_width_times_height_times_6000(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_739_times_1325_plus_image_type_times_6700_plus_width_times_height_times_6000(GRAY) >
                xcf_file_size_mod_739_times_1325_plus_image_type_times_6700_plus_width_times_height_times_6000(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_739_times_1325_plus_image_type_times_6700_plus_width_times_height_times_6000(str(RED)) == 240525


# --- F2: xcf_file_size_mod_743_times_1275_plus_image_type_times_2850_plus_layer_count_times_6700 ---

class TestXcfFileSizeMod743Times1275PlusImageType2850PlusLayerCount6700:
    def test_red_returns_232375(self):
        assert xcf_file_size_mod_743_times_1275_plus_image_type_times_2850_plus_layer_count_times_6700(RED) == 232375

    def test_blue_returns_233650(self):
        assert xcf_file_size_mod_743_times_1275_plus_image_type_times_2850_plus_layer_count_times_6700(BLUE) == 233650

    def test_gray_returns_236500(self):
        assert xcf_file_size_mod_743_times_1275_plus_image_type_times_2850_plus_layer_count_times_6700(GRAY) == 236500

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_743_times_1275_plus_image_type_times_2850_plus_layer_count_times_6700(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_743_times_1275_plus_image_type_times_2850_plus_layer_count_times_6700(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_743_times_1275_plus_image_type_times_2850_plus_layer_count_times_6700(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_743_times_1275_plus_image_type_times_2850_plus_layer_count_times_6700(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_743_times_1275_plus_image_type_times_2850_plus_layer_count_times_6700(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_743_times_1275_plus_image_type_times_2850_plus_layer_count_times_6700(GRAY) >
                xcf_file_size_mod_743_times_1275_plus_image_type_times_2850_plus_layer_count_times_6700(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_743_times_1275_plus_image_type_times_2850_plus_layer_count_times_6700(str(RED)) == 232375
