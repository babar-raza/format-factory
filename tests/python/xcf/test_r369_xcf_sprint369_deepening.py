"""Sprint 369 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_467_times_825_plus_image_type_times_4700_plus_width_times_height_times_4000,
    xcf_file_size_mod_479_times_775_plus_image_type_times_1850_plus_layer_count_times_4700,
)


# --- F1: xcf_file_size_mod_467_times_825_plus_image_type_times_4700_plus_width_times_height_times_4000 ---

class TestXcfFileSizeMod467Times825PlusImageType4700PlusWidthHeight4000:
    def test_red_returns_150025(self):
        assert xcf_file_size_mod_467_times_825_plus_image_type_times_4700_plus_width_times_height_times_4000(RED) == 150025

    def test_blue_returns_150850(self):
        assert xcf_file_size_mod_467_times_825_plus_image_type_times_4700_plus_width_times_height_times_4000(BLUE) == 150850

    def test_gray_returns_167550(self):
        assert xcf_file_size_mod_467_times_825_plus_image_type_times_4700_plus_width_times_height_times_4000(GRAY) == 167550

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_467_times_825_plus_image_type_times_4700_plus_width_times_height_times_4000(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_467_times_825_plus_image_type_times_4700_plus_width_times_height_times_4000(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_467_times_825_plus_image_type_times_4700_plus_width_times_height_times_4000(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_467_times_825_plus_image_type_times_4700_plus_width_times_height_times_4000(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_467_times_825_plus_image_type_times_4700_plus_width_times_height_times_4000(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_467_times_825_plus_image_type_times_4700_plus_width_times_height_times_4000(GRAY) >
                xcf_file_size_mod_467_times_825_plus_image_type_times_4700_plus_width_times_height_times_4000(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_467_times_825_plus_image_type_times_4700_plus_width_times_height_times_4000(str(RED)) == 150025


# --- F2: xcf_file_size_mod_479_times_775_plus_image_type_times_1850_plus_layer_count_times_4700 ---

class TestXcfFileSizeMod479Times775PlusImageType1850PlusLayerCount4700:
    def test_red_returns_141875(self):
        assert xcf_file_size_mod_479_times_775_plus_image_type_times_1850_plus_layer_count_times_4700(RED) == 141875

    def test_blue_returns_142650(self):
        assert xcf_file_size_mod_479_times_775_plus_image_type_times_1850_plus_layer_count_times_4700(BLUE) == 142650

    def test_gray_returns_144500(self):
        assert xcf_file_size_mod_479_times_775_plus_image_type_times_1850_plus_layer_count_times_4700(GRAY) == 144500

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_479_times_775_plus_image_type_times_1850_plus_layer_count_times_4700(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_479_times_775_plus_image_type_times_1850_plus_layer_count_times_4700(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_479_times_775_plus_image_type_times_1850_plus_layer_count_times_4700(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_479_times_775_plus_image_type_times_1850_plus_layer_count_times_4700(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_479_times_775_plus_image_type_times_1850_plus_layer_count_times_4700(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_479_times_775_plus_image_type_times_1850_plus_layer_count_times_4700(GRAY) >
                xcf_file_size_mod_479_times_775_plus_image_type_times_1850_plus_layer_count_times_4700(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_479_times_775_plus_image_type_times_1850_plus_layer_count_times_4700(str(RED)) == 141875
