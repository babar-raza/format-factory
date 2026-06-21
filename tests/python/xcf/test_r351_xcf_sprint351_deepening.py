"""Sprint 351 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_401_times_675_plus_image_type_times_4100_plus_width_times_height_times_3400,
    xcf_file_size_mod_409_times_625_plus_image_type_times_1550_plus_layer_count_times_4100,
)


# --- F1: xcf_file_size_mod_401_times_675_plus_image_type_times_4100_plus_width_times_height_times_3400 ---

class TestXcfFileSizeMod401Times675PlusImageType4100PlusWidthHeight3400:
    def test_red_returns_122875(self):
        assert xcf_file_size_mod_401_times_675_plus_image_type_times_4100_plus_width_times_height_times_3400(RED) == 122875

    def test_blue_returns_123550(self):
        assert xcf_file_size_mod_401_times_675_plus_image_type_times_4100_plus_width_times_height_times_3400(BLUE) == 123550

    def test_gray_returns_137850(self):
        assert xcf_file_size_mod_401_times_675_plus_image_type_times_4100_plus_width_times_height_times_3400(GRAY) == 137850

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_401_times_675_plus_image_type_times_4100_plus_width_times_height_times_3400(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_401_times_675_plus_image_type_times_4100_plus_width_times_height_times_3400(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_401_times_675_plus_image_type_times_4100_plus_width_times_height_times_3400(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_401_times_675_plus_image_type_times_4100_plus_width_times_height_times_3400(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_401_times_675_plus_image_type_times_4100_plus_width_times_height_times_3400(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_401_times_675_plus_image_type_times_4100_plus_width_times_height_times_3400(GRAY) >
                xcf_file_size_mod_401_times_675_plus_image_type_times_4100_plus_width_times_height_times_3400(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_401_times_675_plus_image_type_times_4100_plus_width_times_height_times_3400(str(RED)) == 122875


# --- F2: xcf_file_size_mod_409_times_625_plus_image_type_times_1550_plus_layer_count_times_4100 ---

class TestXcfFileSizeMod409Times625PlusImageType1550PlusLayerCount4100:
    def test_red_returns_114725(self):
        assert xcf_file_size_mod_409_times_625_plus_image_type_times_1550_plus_layer_count_times_4100(RED) == 114725

    def test_blue_returns_115350(self):
        assert xcf_file_size_mod_409_times_625_plus_image_type_times_1550_plus_layer_count_times_4100(BLUE) == 115350

    def test_gray_returns_116900(self):
        assert xcf_file_size_mod_409_times_625_plus_image_type_times_1550_plus_layer_count_times_4100(GRAY) == 116900

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_409_times_625_plus_image_type_times_1550_plus_layer_count_times_4100(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_409_times_625_plus_image_type_times_1550_plus_layer_count_times_4100(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_409_times_625_plus_image_type_times_1550_plus_layer_count_times_4100(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_409_times_625_plus_image_type_times_1550_plus_layer_count_times_4100(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_409_times_625_plus_image_type_times_1550_plus_layer_count_times_4100(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_409_times_625_plus_image_type_times_1550_plus_layer_count_times_4100(GRAY) >
                xcf_file_size_mod_409_times_625_plus_image_type_times_1550_plus_layer_count_times_4100(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_409_times_625_plus_image_type_times_1550_plus_layer_count_times_4100(str(RED)) == 114725
