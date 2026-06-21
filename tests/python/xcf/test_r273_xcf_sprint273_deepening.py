"""Sprint 273 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_53_times_350_plus_image_type_times_1200_plus_width_times_height_times_700,
    xcf_file_size_mod_37_times_200_plus_image_type_times_900_plus_layer_count_times_1000,
)


# --- F1: xcf_file_size_mod_53_times_350_plus_image_type_times_1200_plus_width_times_height_times_700 ---

class TestXcfFileSizeMod53Times350PlusImageType1200PlusWidthTimesHeight700:
    def test_red_returns_7000(self):
        assert xcf_file_size_mod_53_times_350_plus_image_type_times_1200_plus_width_times_height_times_700(RED) == 7000

    def test_blue_returns_7350(self):
        assert xcf_file_size_mod_53_times_350_plus_image_type_times_1200_plus_width_times_height_times_700(BLUE) == 7350

    def test_gray_returns_10650(self):
        assert xcf_file_size_mod_53_times_350_plus_image_type_times_1200_plus_width_times_height_times_700(GRAY) == 10650

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_53_times_350_plus_image_type_times_1200_plus_width_times_height_times_700(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_53_times_350_plus_image_type_times_1200_plus_width_times_height_times_700(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_53_times_350_plus_image_type_times_1200_plus_width_times_height_times_700(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_53_times_350_plus_image_type_times_1200_plus_width_times_height_times_700(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_53_times_350_plus_image_type_times_1200_plus_width_times_height_times_700(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_53_times_350_plus_image_type_times_1200_plus_width_times_height_times_700(GRAY) >
                xcf_file_size_mod_53_times_350_plus_image_type_times_1200_plus_width_times_height_times_700(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_53_times_350_plus_image_type_times_1200_plus_width_times_height_times_700(str(RED)) == 7000


# --- F2: xcf_file_size_mod_37_times_200_plus_image_type_times_900_plus_layer_count_times_1000 ---

class TestXcfFileSizeMod37Times200PlusImageType900PlusLayerCount1000:
    def test_red_returns_6800(self):
        assert xcf_file_size_mod_37_times_200_plus_image_type_times_900_plus_layer_count_times_1000(RED) == 6800

    def test_blue_returns_7000(self):
        assert xcf_file_size_mod_37_times_200_plus_image_type_times_900_plus_layer_count_times_1000(BLUE) == 7000

    def test_gray_returns_7900(self):
        assert xcf_file_size_mod_37_times_200_plus_image_type_times_900_plus_layer_count_times_1000(GRAY) == 7900

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_37_times_200_plus_image_type_times_900_plus_layer_count_times_1000(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_37_times_200_plus_image_type_times_900_plus_layer_count_times_1000(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_37_times_200_plus_image_type_times_900_plus_layer_count_times_1000(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_37_times_200_plus_image_type_times_900_plus_layer_count_times_1000(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_37_times_200_plus_image_type_times_900_plus_layer_count_times_1000(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_37_times_200_plus_image_type_times_900_plus_layer_count_times_1000(GRAY) >
                xcf_file_size_mod_37_times_200_plus_image_type_times_900_plus_layer_count_times_1000(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_37_times_200_plus_image_type_times_900_plus_layer_count_times_1000(str(RED)) == 6800
