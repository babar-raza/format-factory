"""Sprint 321 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_277_times_425_plus_image_type_times_3100_plus_width_times_height_times_2400,
    xcf_file_size_mod_281_times_375_plus_image_type_times_1050_plus_layer_count_times_3100,
)


# --- F1: xcf_file_size_mod_277_times_425_plus_image_type_times_3100_plus_width_times_height_times_2400 ---

class TestXcfFileSizeMod277Times425PlusImageType3100PlusWidthHeight2400:
    def test_red_returns_77625(self):
        assert xcf_file_size_mod_277_times_425_plus_image_type_times_3100_plus_width_times_height_times_2400(RED) == 77625

    def test_blue_returns_78050(self):
        assert xcf_file_size_mod_277_times_425_plus_image_type_times_3100_plus_width_times_height_times_2400(BLUE) == 78050

    def test_gray_returns_88350(self):
        assert xcf_file_size_mod_277_times_425_plus_image_type_times_3100_plus_width_times_height_times_2400(GRAY) == 88350

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_277_times_425_plus_image_type_times_3100_plus_width_times_height_times_2400(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_277_times_425_plus_image_type_times_3100_plus_width_times_height_times_2400(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_277_times_425_plus_image_type_times_3100_plus_width_times_height_times_2400(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_277_times_425_plus_image_type_times_3100_plus_width_times_height_times_2400(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_277_times_425_plus_image_type_times_3100_plus_width_times_height_times_2400(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_277_times_425_plus_image_type_times_3100_plus_width_times_height_times_2400(GRAY) >
                xcf_file_size_mod_277_times_425_plus_image_type_times_3100_plus_width_times_height_times_2400(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_277_times_425_plus_image_type_times_3100_plus_width_times_height_times_2400(str(RED)) == 77625


# --- F2: xcf_file_size_mod_281_times_375_plus_image_type_times_1050_plus_layer_count_times_3100 ---

class TestXcfFileSizeMod281Times375PlusImageType1050PlusLayerCount3100:
    def test_red_returns_69475(self):
        assert xcf_file_size_mod_281_times_375_plus_image_type_times_1050_plus_layer_count_times_3100(RED) == 69475

    def test_blue_returns_69850(self):
        assert xcf_file_size_mod_281_times_375_plus_image_type_times_1050_plus_layer_count_times_3100(BLUE) == 69850

    def test_gray_returns_70900(self):
        assert xcf_file_size_mod_281_times_375_plus_image_type_times_1050_plus_layer_count_times_3100(GRAY) == 70900

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_281_times_375_plus_image_type_times_1050_plus_layer_count_times_3100(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_281_times_375_plus_image_type_times_1050_plus_layer_count_times_3100(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_281_times_375_plus_image_type_times_1050_plus_layer_count_times_3100(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_281_times_375_plus_image_type_times_1050_plus_layer_count_times_3100(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_281_times_375_plus_image_type_times_1050_plus_layer_count_times_3100(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_281_times_375_plus_image_type_times_1050_plus_layer_count_times_3100(GRAY) >
                xcf_file_size_mod_281_times_375_plus_image_type_times_1050_plus_layer_count_times_3100(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_281_times_375_plus_image_type_times_1050_plus_layer_count_times_3100(str(RED)) == 69475
