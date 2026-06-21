"""Sprint 285 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_11_times_150_plus_image_type_times_1800_plus_width_times_height_times_1100,
    xcf_file_size_mod_7_times_75_plus_image_type_times_400_plus_layer_count_times_1800,
)


# --- F1: xcf_file_size_mod_11_times_150_plus_image_type_times_1800_plus_width_times_height_times_1100 ---

class TestXcfFileSizeMod11Times150PlusImageType1800PlusWidthTimesHeight1100:
    def test_red_returns_1250(self):
        assert xcf_file_size_mod_11_times_150_plus_image_type_times_1800_plus_width_times_height_times_1100(RED) == 1250

    def test_blue_returns_1400(self):
        assert xcf_file_size_mod_11_times_150_plus_image_type_times_1800_plus_width_times_height_times_1100(BLUE) == 1400

    def test_gray_returns_6500(self):
        assert xcf_file_size_mod_11_times_150_plus_image_type_times_1800_plus_width_times_height_times_1100(GRAY) == 6500

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_11_times_150_plus_image_type_times_1800_plus_width_times_height_times_1100(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_11_times_150_plus_image_type_times_1800_plus_width_times_height_times_1100(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_11_times_150_plus_image_type_times_1800_plus_width_times_height_times_1100(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_11_times_150_plus_image_type_times_1800_plus_width_times_height_times_1100(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_11_times_150_plus_image_type_times_1800_plus_width_times_height_times_1100(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_11_times_150_plus_image_type_times_1800_plus_width_times_height_times_1100(GRAY) >
                xcf_file_size_mod_11_times_150_plus_image_type_times_1800_plus_width_times_height_times_1100(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_11_times_150_plus_image_type_times_1800_plus_width_times_height_times_1100(str(RED)) == 1250


# --- F2: xcf_file_size_mod_7_times_75_plus_image_type_times_400_plus_layer_count_times_1800 ---

class TestXcfFileSizeMod7Times75PlusImageType400PlusLayerCount1800:
    def test_red_returns_1950(self):
        assert xcf_file_size_mod_7_times_75_plus_image_type_times_400_plus_layer_count_times_1800(RED) == 1950

    def test_blue_returns_2025(self):
        assert xcf_file_size_mod_7_times_75_plus_image_type_times_400_plus_layer_count_times_1800(BLUE) == 2025

    def test_gray_returns_2425(self):
        assert xcf_file_size_mod_7_times_75_plus_image_type_times_400_plus_layer_count_times_1800(GRAY) == 2425

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_7_times_75_plus_image_type_times_400_plus_layer_count_times_1800(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_7_times_75_plus_image_type_times_400_plus_layer_count_times_1800(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_7_times_75_plus_image_type_times_400_plus_layer_count_times_1800(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_7_times_75_plus_image_type_times_400_plus_layer_count_times_1800(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_7_times_75_plus_image_type_times_400_plus_layer_count_times_1800(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_7_times_75_plus_image_type_times_400_plus_layer_count_times_1800(GRAY) >
                xcf_file_size_mod_7_times_75_plus_image_type_times_400_plus_layer_count_times_1800(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_7_times_75_plus_image_type_times_400_plus_layer_count_times_1800(str(RED)) == 1950
