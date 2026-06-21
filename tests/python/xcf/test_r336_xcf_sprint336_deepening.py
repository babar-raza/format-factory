"""Sprint 336 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_347_times_550_plus_image_type_times_3600_plus_width_times_height_times_2900,
    xcf_file_size_mod_349_times_500_plus_image_type_times_1300_plus_layer_count_times_3600,
)


# --- F1: xcf_file_size_mod_347_times_550_plus_image_type_times_3600_plus_width_times_height_times_2900 ---

class TestXcfFileSizeMod347Times550PlusImageType3600PlusWidthHeight2900:
    def test_red_returns_100250(self):
        assert xcf_file_size_mod_347_times_550_plus_image_type_times_3600_plus_width_times_height_times_2900(RED) == 100250

    def test_blue_returns_100800(self):
        assert xcf_file_size_mod_347_times_550_plus_image_type_times_3600_plus_width_times_height_times_2900(BLUE) == 100800

    def test_gray_returns_113100(self):
        assert xcf_file_size_mod_347_times_550_plus_image_type_times_3600_plus_width_times_height_times_2900(GRAY) == 113100

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_347_times_550_plus_image_type_times_3600_plus_width_times_height_times_2900(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_347_times_550_plus_image_type_times_3600_plus_width_times_height_times_2900(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_347_times_550_plus_image_type_times_3600_plus_width_times_height_times_2900(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_347_times_550_plus_image_type_times_3600_plus_width_times_height_times_2900(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_347_times_550_plus_image_type_times_3600_plus_width_times_height_times_2900(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_347_times_550_plus_image_type_times_3600_plus_width_times_height_times_2900(GRAY) >
                xcf_file_size_mod_347_times_550_plus_image_type_times_3600_plus_width_times_height_times_2900(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_347_times_550_plus_image_type_times_3600_plus_width_times_height_times_2900(str(RED)) == 100250


# --- F2: xcf_file_size_mod_349_times_500_plus_image_type_times_1300_plus_layer_count_times_3600 ---

class TestXcfFileSizeMod349Times500PlusImageType1300PlusLayerCount3600:
    def test_red_returns_92100(self):
        assert xcf_file_size_mod_349_times_500_plus_image_type_times_1300_plus_layer_count_times_3600(RED) == 92100

    def test_blue_returns_92600(self):
        assert xcf_file_size_mod_349_times_500_plus_image_type_times_1300_plus_layer_count_times_3600(BLUE) == 92600

    def test_gray_returns_93900(self):
        assert xcf_file_size_mod_349_times_500_plus_image_type_times_1300_plus_layer_count_times_3600(GRAY) == 93900

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_349_times_500_plus_image_type_times_1300_plus_layer_count_times_3600(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_349_times_500_plus_image_type_times_1300_plus_layer_count_times_3600(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_349_times_500_plus_image_type_times_1300_plus_layer_count_times_3600(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_349_times_500_plus_image_type_times_1300_plus_layer_count_times_3600(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_349_times_500_plus_image_type_times_1300_plus_layer_count_times_3600(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_349_times_500_plus_image_type_times_1300_plus_layer_count_times_3600(GRAY) >
                xcf_file_size_mod_349_times_500_plus_image_type_times_1300_plus_layer_count_times_3600(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_349_times_500_plus_image_type_times_1300_plus_layer_count_times_3600(str(RED)) == 92100
