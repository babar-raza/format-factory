"""Sprint 318 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_269_times_400_plus_image_type_times_3000_plus_width_times_height_times_2300,
    xcf_file_size_mod_271_times_350_plus_image_type_times_1000_plus_layer_count_times_3000,
)


# --- F1: xcf_file_size_mod_269_times_400_plus_image_type_times_3000_plus_width_times_height_times_2300 ---

class TestXcfFileSizeMod269Times400PlusImageType3000PlusWidthHeight2300:
    def test_red_returns_73100(self):
        assert xcf_file_size_mod_269_times_400_plus_image_type_times_3000_plus_width_times_height_times_2300(RED) == 73100

    def test_blue_returns_73500(self):
        assert xcf_file_size_mod_269_times_400_plus_image_type_times_3000_plus_width_times_height_times_2300(BLUE) == 73500

    def test_gray_returns_83400(self):
        assert xcf_file_size_mod_269_times_400_plus_image_type_times_3000_plus_width_times_height_times_2300(GRAY) == 83400

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_269_times_400_plus_image_type_times_3000_plus_width_times_height_times_2300(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_269_times_400_plus_image_type_times_3000_plus_width_times_height_times_2300(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_269_times_400_plus_image_type_times_3000_plus_width_times_height_times_2300(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_269_times_400_plus_image_type_times_3000_plus_width_times_height_times_2300(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_269_times_400_plus_image_type_times_3000_plus_width_times_height_times_2300(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_269_times_400_plus_image_type_times_3000_plus_width_times_height_times_2300(GRAY) >
                xcf_file_size_mod_269_times_400_plus_image_type_times_3000_plus_width_times_height_times_2300(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_269_times_400_plus_image_type_times_3000_plus_width_times_height_times_2300(str(RED)) == 73100


# --- F2: xcf_file_size_mod_271_times_350_plus_image_type_times_1000_plus_layer_count_times_3000 ---

class TestXcfFileSizeMod271Times350PlusImageType1000PlusLayerCount3000:
    def test_red_returns_64950(self):
        assert xcf_file_size_mod_271_times_350_plus_image_type_times_1000_plus_layer_count_times_3000(RED) == 64950

    def test_blue_returns_65300(self):
        assert xcf_file_size_mod_271_times_350_plus_image_type_times_1000_plus_layer_count_times_3000(BLUE) == 65300

    def test_gray_returns_66300(self):
        assert xcf_file_size_mod_271_times_350_plus_image_type_times_1000_plus_layer_count_times_3000(GRAY) == 66300

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_271_times_350_plus_image_type_times_1000_plus_layer_count_times_3000(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_271_times_350_plus_image_type_times_1000_plus_layer_count_times_3000(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_271_times_350_plus_image_type_times_1000_plus_layer_count_times_3000(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_271_times_350_plus_image_type_times_1000_plus_layer_count_times_3000(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_271_times_350_plus_image_type_times_1000_plus_layer_count_times_3000(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_271_times_350_plus_image_type_times_1000_plus_layer_count_times_3000(GRAY) >
                xcf_file_size_mod_271_times_350_plus_image_type_times_1000_plus_layer_count_times_3000(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_271_times_350_plus_image_type_times_1000_plus_layer_count_times_3000(str(RED)) == 64950
