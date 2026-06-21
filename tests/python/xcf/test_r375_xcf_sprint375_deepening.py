"""Sprint 375 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_499_times_875_plus_image_type_times_4900_plus_width_times_height_times_4200,
    xcf_file_size_mod_503_times_825_plus_image_type_times_1950_plus_layer_count_times_4900,
)


# --- F1: xcf_file_size_mod_499_times_875_plus_image_type_times_4900_plus_width_times_height_times_4200 ---

class TestXcfFileSizeMod499Times875PlusImageType4900PlusWidthHeight4200:
    def test_red_returns_159075(self):
        assert xcf_file_size_mod_499_times_875_plus_image_type_times_4900_plus_width_times_height_times_4200(RED) == 159075

    def test_blue_returns_159950(self):
        assert xcf_file_size_mod_499_times_875_plus_image_type_times_4900_plus_width_times_height_times_4200(BLUE) == 159950

    def test_gray_returns_177450(self):
        assert xcf_file_size_mod_499_times_875_plus_image_type_times_4900_plus_width_times_height_times_4200(GRAY) == 177450

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_499_times_875_plus_image_type_times_4900_plus_width_times_height_times_4200(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_499_times_875_plus_image_type_times_4900_plus_width_times_height_times_4200(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_499_times_875_plus_image_type_times_4900_plus_width_times_height_times_4200(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_499_times_875_plus_image_type_times_4900_plus_width_times_height_times_4200(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_499_times_875_plus_image_type_times_4900_plus_width_times_height_times_4200(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_499_times_875_plus_image_type_times_4900_plus_width_times_height_times_4200(GRAY) >
                xcf_file_size_mod_499_times_875_plus_image_type_times_4900_plus_width_times_height_times_4200(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_499_times_875_plus_image_type_times_4900_plus_width_times_height_times_4200(str(RED)) == 159075


# --- F2: xcf_file_size_mod_503_times_825_plus_image_type_times_1950_plus_layer_count_times_4900 ---

class TestXcfFileSizeMod503Times825PlusImageType1950PlusLayerCount4900:
    def test_red_returns_150925(self):
        assert xcf_file_size_mod_503_times_825_plus_image_type_times_1950_plus_layer_count_times_4900(RED) == 150925

    def test_blue_returns_151750(self):
        assert xcf_file_size_mod_503_times_825_plus_image_type_times_1950_plus_layer_count_times_4900(BLUE) == 151750

    def test_gray_returns_153700(self):
        assert xcf_file_size_mod_503_times_825_plus_image_type_times_1950_plus_layer_count_times_4900(GRAY) == 153700

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_503_times_825_plus_image_type_times_1950_plus_layer_count_times_4900(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_503_times_825_plus_image_type_times_1950_plus_layer_count_times_4900(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_503_times_825_plus_image_type_times_1950_plus_layer_count_times_4900(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_503_times_825_plus_image_type_times_1950_plus_layer_count_times_4900(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_503_times_825_plus_image_type_times_1950_plus_layer_count_times_4900(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_503_times_825_plus_image_type_times_1950_plus_layer_count_times_4900(GRAY) >
                xcf_file_size_mod_503_times_825_plus_image_type_times_1950_plus_layer_count_times_4900(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_503_times_825_plus_image_type_times_1950_plus_layer_count_times_4900(str(RED)) == 150925
