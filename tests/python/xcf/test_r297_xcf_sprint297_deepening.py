"""Sprint 297 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_149_times_350_plus_image_type_times_2200_plus_width_times_height_times_1500,
    xcf_file_size_mod_151_times_175_plus_image_type_times_600_plus_layer_count_times_2200,
)


# --- F1: xcf_file_size_mod_149_times_350_plus_image_type_times_2200_plus_width_times_height_times_1500 ---

class TestXcfFileSizeMod149Times350PlusImageType2200PlusWidthTimesHeight1500:
    def test_red_returns_11300(self):
        assert xcf_file_size_mod_149_times_350_plus_image_type_times_2200_plus_width_times_height_times_1500(RED) == 11300

    def test_blue_returns_11650(self):
        assert xcf_file_size_mod_149_times_350_plus_image_type_times_2200_plus_width_times_height_times_1500(BLUE) == 11650

    def test_gray_returns_18350(self):
        assert xcf_file_size_mod_149_times_350_plus_image_type_times_2200_plus_width_times_height_times_1500(GRAY) == 18350

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_149_times_350_plus_image_type_times_2200_plus_width_times_height_times_1500(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_149_times_350_plus_image_type_times_2200_plus_width_times_height_times_1500(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_149_times_350_plus_image_type_times_2200_plus_width_times_height_times_1500(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_149_times_350_plus_image_type_times_2200_plus_width_times_height_times_1500(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_149_times_350_plus_image_type_times_2200_plus_width_times_height_times_1500(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_149_times_350_plus_image_type_times_2200_plus_width_times_height_times_1500(GRAY) >
                xcf_file_size_mod_149_times_350_plus_image_type_times_2200_plus_width_times_height_times_1500(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_149_times_350_plus_image_type_times_2200_plus_width_times_height_times_1500(str(RED)) == 11300


# --- F2: xcf_file_size_mod_151_times_175_plus_image_type_times_600_plus_layer_count_times_2200 ---

class TestXcfFileSizeMod151Times175PlusImageType600PlusLayerCount2200:
    def test_red_returns_6750(self):
        assert xcf_file_size_mod_151_times_175_plus_image_type_times_600_plus_layer_count_times_2200(RED) == 6750

    def test_blue_returns_6925(self):
        assert xcf_file_size_mod_151_times_175_plus_image_type_times_600_plus_layer_count_times_2200(BLUE) == 6925

    def test_gray_returns_7525(self):
        assert xcf_file_size_mod_151_times_175_plus_image_type_times_600_plus_layer_count_times_2200(GRAY) == 7525

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_151_times_175_plus_image_type_times_600_plus_layer_count_times_2200(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_151_times_175_plus_image_type_times_600_plus_layer_count_times_2200(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_151_times_175_plus_image_type_times_600_plus_layer_count_times_2200(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_151_times_175_plus_image_type_times_600_plus_layer_count_times_2200(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_151_times_175_plus_image_type_times_600_plus_layer_count_times_2200(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_151_times_175_plus_image_type_times_600_plus_layer_count_times_2200(GRAY) >
                xcf_file_size_mod_151_times_175_plus_image_type_times_600_plus_layer_count_times_2200(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_151_times_175_plus_image_type_times_600_plus_layer_count_times_2200(str(RED)) == 6750
