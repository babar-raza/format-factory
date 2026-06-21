"""Sprint 264 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_41_times_200_plus_image_type_times_1200_plus_width_times_height_times_300,
    xcf_file_size_mod_19_times_300_plus_image_type_times_900_plus_layer_count_times_700,
)


# --- F1: xcf_file_size_mod_41_times_200_plus_image_type_times_1200_plus_width_times_height_times_300 ---

class TestXcfFileSizeMod41Times200PlusImageType1200PlusWidthHeightTimes300:
    def test_red_returns_2900(self):
        assert xcf_file_size_mod_41_times_200_plus_image_type_times_1200_plus_width_times_height_times_300(RED) == 2900

    def test_blue_returns_3100(self):
        assert xcf_file_size_mod_41_times_200_plus_image_type_times_1200_plus_width_times_height_times_300(BLUE) == 3100

    def test_gray_returns_5200(self):
        assert xcf_file_size_mod_41_times_200_plus_image_type_times_1200_plus_width_times_height_times_300(GRAY) == 5200

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_41_times_200_plus_image_type_times_1200_plus_width_times_height_times_300(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_41_times_200_plus_image_type_times_1200_plus_width_times_height_times_300(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_41_times_200_plus_image_type_times_1200_plus_width_times_height_times_300(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_41_times_200_plus_image_type_times_1200_plus_width_times_height_times_300(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_41_times_200_plus_image_type_times_1200_plus_width_times_height_times_300(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_41_times_200_plus_image_type_times_1200_plus_width_times_height_times_300(GRAY) >
                xcf_file_size_mod_41_times_200_plus_image_type_times_1200_plus_width_times_height_times_300(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_41_times_200_plus_image_type_times_1200_plus_width_times_height_times_300(str(RED)) == 2900


# --- F2: xcf_file_size_mod_19_times_300_plus_image_type_times_900_plus_layer_count_times_700 ---

class TestXcfFileSizeMod19Times300PlusImageType900PlusLayerCount700:
    def test_red_returns_2500(self):
        assert xcf_file_size_mod_19_times_300_plus_image_type_times_900_plus_layer_count_times_700(RED) == 2500

    def test_blue_returns_2800(self):
        assert xcf_file_size_mod_19_times_300_plus_image_type_times_900_plus_layer_count_times_700(BLUE) == 2800

    def test_gray_returns_3700(self):
        assert xcf_file_size_mod_19_times_300_plus_image_type_times_900_plus_layer_count_times_700(GRAY) == 3700

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_19_times_300_plus_image_type_times_900_plus_layer_count_times_700(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_19_times_300_plus_image_type_times_900_plus_layer_count_times_700(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_19_times_300_plus_image_type_times_900_plus_layer_count_times_700(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_19_times_300_plus_image_type_times_900_plus_layer_count_times_700(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_19_times_300_plus_image_type_times_900_plus_layer_count_times_700(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_19_times_300_plus_image_type_times_900_plus_layer_count_times_700(GRAY) >
                xcf_file_size_mod_19_times_300_plus_image_type_times_900_plus_layer_count_times_700(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_19_times_300_plus_image_type_times_900_plus_layer_count_times_700(str(RED)) == 2500
