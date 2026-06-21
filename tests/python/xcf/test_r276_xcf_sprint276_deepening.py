"""Sprint 276 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_41_times_300_plus_image_type_times_1500_plus_width_times_height_times_800,
    xcf_file_size_mod_31_times_150_plus_image_type_times_700_plus_layer_count_times_1200,
)


# --- F1: xcf_file_size_mod_41_times_300_plus_image_type_times_1500_plus_width_times_height_times_800 ---

class TestXcfFileSizeMod41Times300PlusImageType1500PlusWidthTimesHeight800:
    def test_red_returns_4700(self):
        assert xcf_file_size_mod_41_times_300_plus_image_type_times_1500_plus_width_times_height_times_800(RED) == 4700

    def test_blue_returns_5000(self):
        assert xcf_file_size_mod_41_times_300_plus_image_type_times_1500_plus_width_times_height_times_800(BLUE) == 5000

    def test_gray_returns_8900(self):
        assert xcf_file_size_mod_41_times_300_plus_image_type_times_1500_plus_width_times_height_times_800(GRAY) == 8900

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_41_times_300_plus_image_type_times_1500_plus_width_times_height_times_800(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_41_times_300_plus_image_type_times_1500_plus_width_times_height_times_800(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_41_times_300_plus_image_type_times_1500_plus_width_times_height_times_800(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_41_times_300_plus_image_type_times_1500_plus_width_times_height_times_800(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_41_times_300_plus_image_type_times_1500_plus_width_times_height_times_800(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_41_times_300_plus_image_type_times_1500_plus_width_times_height_times_800(GRAY) >
                xcf_file_size_mod_41_times_300_plus_image_type_times_1500_plus_width_times_height_times_800(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_41_times_300_plus_image_type_times_1500_plus_width_times_height_times_800(str(RED)) == 4700


# --- F2: xcf_file_size_mod_31_times_150_plus_image_type_times_700_plus_layer_count_times_1200 ---

class TestXcfFileSizeMod31Times150PlusImageType700PlusLayerCount1200:
    def test_red_returns_4500(self):
        assert xcf_file_size_mod_31_times_150_plus_image_type_times_700_plus_layer_count_times_1200(RED) == 4500

    def test_blue_returns_4650(self):
        assert xcf_file_size_mod_31_times_150_plus_image_type_times_700_plus_layer_count_times_1200(BLUE) == 4650

    def test_gray_returns_5350(self):
        assert xcf_file_size_mod_31_times_150_plus_image_type_times_700_plus_layer_count_times_1200(GRAY) == 5350

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_31_times_150_plus_image_type_times_700_plus_layer_count_times_1200(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_31_times_150_plus_image_type_times_700_plus_layer_count_times_1200(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_31_times_150_plus_image_type_times_700_plus_layer_count_times_1200(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_31_times_150_plus_image_type_times_700_plus_layer_count_times_1200(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_31_times_150_plus_image_type_times_700_plus_layer_count_times_1200(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_31_times_150_plus_image_type_times_700_plus_layer_count_times_1200(GRAY) >
                xcf_file_size_mod_31_times_150_plus_image_type_times_700_plus_layer_count_times_1200(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_31_times_150_plus_image_type_times_700_plus_layer_count_times_1200(str(RED)) == 4500
