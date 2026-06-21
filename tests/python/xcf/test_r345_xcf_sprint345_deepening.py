"""Sprint 345 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_379_times_625_plus_image_type_times_3900_plus_width_times_height_times_3200,
    xcf_file_size_mod_383_times_575_plus_image_type_times_1450_plus_layer_count_times_3900,
)


# --- F1: xcf_file_size_mod_379_times_625_plus_image_type_times_3900_plus_width_times_height_times_3200 ---

class TestXcfFileSizeMod379Times625PlusImageType3900PlusWidthHeight3200:
    def test_red_returns_113825(self):
        assert xcf_file_size_mod_379_times_625_plus_image_type_times_3900_plus_width_times_height_times_3200(RED) == 113825

    def test_blue_returns_114450(self):
        assert xcf_file_size_mod_379_times_625_plus_image_type_times_3900_plus_width_times_height_times_3200(BLUE) == 114450

    def test_gray_returns_127950(self):
        assert xcf_file_size_mod_379_times_625_plus_image_type_times_3900_plus_width_times_height_times_3200(GRAY) == 127950

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_379_times_625_plus_image_type_times_3900_plus_width_times_height_times_3200(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_379_times_625_plus_image_type_times_3900_plus_width_times_height_times_3200(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_379_times_625_plus_image_type_times_3900_plus_width_times_height_times_3200(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_379_times_625_plus_image_type_times_3900_plus_width_times_height_times_3200(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_379_times_625_plus_image_type_times_3900_plus_width_times_height_times_3200(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_379_times_625_plus_image_type_times_3900_plus_width_times_height_times_3200(GRAY) >
                xcf_file_size_mod_379_times_625_plus_image_type_times_3900_plus_width_times_height_times_3200(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_379_times_625_plus_image_type_times_3900_plus_width_times_height_times_3200(str(RED)) == 113825


# --- F2: xcf_file_size_mod_383_times_575_plus_image_type_times_1450_plus_layer_count_times_3900 ---

class TestXcfFileSizeMod383Times575PlusImageType1450PlusLayerCount3900:
    def test_red_returns_105675(self):
        assert xcf_file_size_mod_383_times_575_plus_image_type_times_1450_plus_layer_count_times_3900(RED) == 105675

    def test_blue_returns_106250(self):
        assert xcf_file_size_mod_383_times_575_plus_image_type_times_1450_plus_layer_count_times_3900(BLUE) == 106250

    def test_gray_returns_107700(self):
        assert xcf_file_size_mod_383_times_575_plus_image_type_times_1450_plus_layer_count_times_3900(GRAY) == 107700

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_383_times_575_plus_image_type_times_1450_plus_layer_count_times_3900(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_383_times_575_plus_image_type_times_1450_plus_layer_count_times_3900(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_383_times_575_plus_image_type_times_1450_plus_layer_count_times_3900(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_383_times_575_plus_image_type_times_1450_plus_layer_count_times_3900(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_383_times_575_plus_image_type_times_1450_plus_layer_count_times_3900(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_383_times_575_plus_image_type_times_1450_plus_layer_count_times_3900(GRAY) >
                xcf_file_size_mod_383_times_575_plus_image_type_times_1450_plus_layer_count_times_3900(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_383_times_575_plus_image_type_times_1450_plus_layer_count_times_3900(str(RED)) == 105675
