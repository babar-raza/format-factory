"""Sprint 288 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_109_times_200_plus_image_type_times_1900_plus_width_times_height_times_1200,
    xcf_file_size_mod_113_times_100_plus_image_type_times_450_plus_layer_count_times_1900,
)


# --- F1: xcf_file_size_mod_109_times_200_plus_image_type_times_1900_plus_width_times_height_times_1200 ---

class TestXcfFileSizeMod109Times200PlusImageType1900PlusWidthTimesHeight1200:
    def test_red_returns_14800(self):
        assert xcf_file_size_mod_109_times_200_plus_image_type_times_1900_plus_width_times_height_times_1200(RED) == 14800

    def test_blue_returns_15000(self):
        assert xcf_file_size_mod_109_times_200_plus_image_type_times_1900_plus_width_times_height_times_1200(BLUE) == 15000

    def test_gray_returns_20500(self):
        assert xcf_file_size_mod_109_times_200_plus_image_type_times_1900_plus_width_times_height_times_1200(GRAY) == 20500

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_109_times_200_plus_image_type_times_1900_plus_width_times_height_times_1200(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_109_times_200_plus_image_type_times_1900_plus_width_times_height_times_1200(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_109_times_200_plus_image_type_times_1900_plus_width_times_height_times_1200(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_109_times_200_plus_image_type_times_1900_plus_width_times_height_times_1200(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_109_times_200_plus_image_type_times_1900_plus_width_times_height_times_1200(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_109_times_200_plus_image_type_times_1900_plus_width_times_height_times_1200(GRAY) >
                xcf_file_size_mod_109_times_200_plus_image_type_times_1900_plus_width_times_height_times_1200(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_109_times_200_plus_image_type_times_1900_plus_width_times_height_times_1200(str(RED)) == 14800


# --- F2: xcf_file_size_mod_113_times_100_plus_image_type_times_450_plus_layer_count_times_1900 ---

class TestXcfFileSizeMod113Times100PlusImageType450PlusLayerCount1900:
    def test_red_returns_8300(self):
        assert xcf_file_size_mod_113_times_100_plus_image_type_times_450_plus_layer_count_times_1900(RED) == 8300

    def test_blue_returns_8400(self):
        assert xcf_file_size_mod_113_times_100_plus_image_type_times_450_plus_layer_count_times_1900(BLUE) == 8400

    def test_gray_returns_8850(self):
        assert xcf_file_size_mod_113_times_100_plus_image_type_times_450_plus_layer_count_times_1900(GRAY) == 8850

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_113_times_100_plus_image_type_times_450_plus_layer_count_times_1900(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_113_times_100_plus_image_type_times_450_plus_layer_count_times_1900(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_113_times_100_plus_image_type_times_450_plus_layer_count_times_1900(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_113_times_100_plus_image_type_times_450_plus_layer_count_times_1900(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_113_times_100_plus_image_type_times_450_plus_layer_count_times_1900(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_113_times_100_plus_image_type_times_450_plus_layer_count_times_1900(GRAY) >
                xcf_file_size_mod_113_times_100_plus_image_type_times_450_plus_layer_count_times_1900(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_113_times_100_plus_image_type_times_450_plus_layer_count_times_1900(str(RED)) == 8300
