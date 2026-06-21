"""Sprint 282 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_13_times_200_plus_image_type_times_1700_plus_width_times_height_times_1000,
    xcf_file_size_mod_17_times_50_plus_image_type_times_500_plus_layer_count_times_1600,
)


# --- F1: xcf_file_size_mod_13_times_200_plus_image_type_times_1700_plus_width_times_height_times_1000 ---

class TestXcfFileSizeMod13Times200PlusImageType1700PlusWidthTimesHeight1000:
    def test_red_returns_2600(self):
        assert xcf_file_size_mod_13_times_200_plus_image_type_times_1700_plus_width_times_height_times_1000(RED) == 2600

    def test_blue_returns_2800(self):
        assert xcf_file_size_mod_13_times_200_plus_image_type_times_1700_plus_width_times_height_times_1000(BLUE) == 2800

    def test_gray_returns_7500(self):
        assert xcf_file_size_mod_13_times_200_plus_image_type_times_1700_plus_width_times_height_times_1000(GRAY) == 7500

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_13_times_200_plus_image_type_times_1700_plus_width_times_height_times_1000(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_13_times_200_plus_image_type_times_1700_plus_width_times_height_times_1000(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_13_times_200_plus_image_type_times_1700_plus_width_times_height_times_1000(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_13_times_200_plus_image_type_times_1700_plus_width_times_height_times_1000(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_13_times_200_plus_image_type_times_1700_plus_width_times_height_times_1000(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_13_times_200_plus_image_type_times_1700_plus_width_times_height_times_1000(GRAY) >
                xcf_file_size_mod_13_times_200_plus_image_type_times_1700_plus_width_times_height_times_1000(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_13_times_200_plus_image_type_times_1700_plus_width_times_height_times_1000(str(RED)) == 2600


# --- F2: xcf_file_size_mod_17_times_50_plus_image_type_times_500_plus_layer_count_times_1600 ---

class TestXcfFileSizeMod17Times50PlusImageType500PlusLayerCount1600:
    def test_red_returns_1950(self):
        assert xcf_file_size_mod_17_times_50_plus_image_type_times_500_plus_layer_count_times_1600(RED) == 1950

    def test_blue_returns_2000(self):
        assert xcf_file_size_mod_17_times_50_plus_image_type_times_500_plus_layer_count_times_1600(BLUE) == 2000

    def test_gray_returns_2500(self):
        assert xcf_file_size_mod_17_times_50_plus_image_type_times_500_plus_layer_count_times_1600(GRAY) == 2500

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_17_times_50_plus_image_type_times_500_plus_layer_count_times_1600(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_17_times_50_plus_image_type_times_500_plus_layer_count_times_1600(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_17_times_50_plus_image_type_times_500_plus_layer_count_times_1600(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_17_times_50_plus_image_type_times_500_plus_layer_count_times_1600(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_17_times_50_plus_image_type_times_500_plus_layer_count_times_1600(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_17_times_50_plus_image_type_times_500_plus_layer_count_times_1600(GRAY) >
                xcf_file_size_mod_17_times_50_plus_image_type_times_500_plus_layer_count_times_1600(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_17_times_50_plus_image_type_times_500_plus_layer_count_times_1600(str(RED)) == 1950
