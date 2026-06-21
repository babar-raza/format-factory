"""Sprint 342 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_367_times_600_plus_image_type_times_3800_plus_width_times_height_times_3100,
    xcf_file_size_mod_373_times_550_plus_image_type_times_1400_plus_layer_count_times_3800,
)


# --- F1: xcf_file_size_mod_367_times_600_plus_image_type_times_3800_plus_width_times_height_times_3100 ---

class TestXcfFileSizeMod367Times600PlusImageType3800PlusWidthHeight3100:
    def test_red_returns_109300(self):
        assert xcf_file_size_mod_367_times_600_plus_image_type_times_3800_plus_width_times_height_times_3100(RED) == 109300

    def test_blue_returns_109900(self):
        assert xcf_file_size_mod_367_times_600_plus_image_type_times_3800_plus_width_times_height_times_3100(BLUE) == 109900

    def test_gray_returns_123000(self):
        assert xcf_file_size_mod_367_times_600_plus_image_type_times_3800_plus_width_times_height_times_3100(GRAY) == 123000

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_367_times_600_plus_image_type_times_3800_plus_width_times_height_times_3100(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_367_times_600_plus_image_type_times_3800_plus_width_times_height_times_3100(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_367_times_600_plus_image_type_times_3800_plus_width_times_height_times_3100(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_367_times_600_plus_image_type_times_3800_plus_width_times_height_times_3100(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_367_times_600_plus_image_type_times_3800_plus_width_times_height_times_3100(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_367_times_600_plus_image_type_times_3800_plus_width_times_height_times_3100(GRAY) >
                xcf_file_size_mod_367_times_600_plus_image_type_times_3800_plus_width_times_height_times_3100(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_367_times_600_plus_image_type_times_3800_plus_width_times_height_times_3100(str(RED)) == 109300


# --- F2: xcf_file_size_mod_373_times_550_plus_image_type_times_1400_plus_layer_count_times_3800 ---

class TestXcfFileSizeMod373Times550PlusImageType1400PlusLayerCount3800:
    def test_red_returns_101150(self):
        assert xcf_file_size_mod_373_times_550_plus_image_type_times_1400_plus_layer_count_times_3800(RED) == 101150

    def test_blue_returns_101700(self):
        assert xcf_file_size_mod_373_times_550_plus_image_type_times_1400_plus_layer_count_times_3800(BLUE) == 101700

    def test_gray_returns_103100(self):
        assert xcf_file_size_mod_373_times_550_plus_image_type_times_1400_plus_layer_count_times_3800(GRAY) == 103100

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_373_times_550_plus_image_type_times_1400_plus_layer_count_times_3800(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_373_times_550_plus_image_type_times_1400_plus_layer_count_times_3800(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_373_times_550_plus_image_type_times_1400_plus_layer_count_times_3800(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_373_times_550_plus_image_type_times_1400_plus_layer_count_times_3800(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_373_times_550_plus_image_type_times_1400_plus_layer_count_times_3800(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_373_times_550_plus_image_type_times_1400_plus_layer_count_times_3800(GRAY) >
                xcf_file_size_mod_373_times_550_plus_image_type_times_1400_plus_layer_count_times_3800(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_373_times_550_plus_image_type_times_1400_plus_layer_count_times_3800(str(RED)) == 101150
