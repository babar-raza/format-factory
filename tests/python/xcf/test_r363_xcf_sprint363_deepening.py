"""Sprint 363 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_449_times_775_plus_image_type_times_4500_plus_width_times_height_times_3800,
    xcf_file_size_mod_457_times_725_plus_image_type_times_1750_plus_layer_count_times_4500,
)


# --- F1: xcf_file_size_mod_449_times_775_plus_image_type_times_4500_plus_width_times_height_times_3800 ---

class TestXcfFileSizeMod449Times775PlusImageType4500PlusWidthHeight3800:
    def test_red_returns_140975(self):
        assert xcf_file_size_mod_449_times_775_plus_image_type_times_4500_plus_width_times_height_times_3800(RED) == 140975

    def test_blue_returns_141750(self):
        assert xcf_file_size_mod_449_times_775_plus_image_type_times_4500_plus_width_times_height_times_3800(BLUE) == 141750

    def test_gray_returns_157650(self):
        assert xcf_file_size_mod_449_times_775_plus_image_type_times_4500_plus_width_times_height_times_3800(GRAY) == 157650

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_449_times_775_plus_image_type_times_4500_plus_width_times_height_times_3800(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_449_times_775_plus_image_type_times_4500_plus_width_times_height_times_3800(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_449_times_775_plus_image_type_times_4500_plus_width_times_height_times_3800(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_449_times_775_plus_image_type_times_4500_plus_width_times_height_times_3800(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_449_times_775_plus_image_type_times_4500_plus_width_times_height_times_3800(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_449_times_775_plus_image_type_times_4500_plus_width_times_height_times_3800(GRAY) >
                xcf_file_size_mod_449_times_775_plus_image_type_times_4500_plus_width_times_height_times_3800(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_449_times_775_plus_image_type_times_4500_plus_width_times_height_times_3800(str(RED)) == 140975


# --- F2: xcf_file_size_mod_457_times_725_plus_image_type_times_1750_plus_layer_count_times_4500 ---

class TestXcfFileSizeMod457Times725PlusImageType1750PlusLayerCount4500:
    def test_red_returns_132825(self):
        assert xcf_file_size_mod_457_times_725_plus_image_type_times_1750_plus_layer_count_times_4500(RED) == 132825

    def test_blue_returns_133550(self):
        assert xcf_file_size_mod_457_times_725_plus_image_type_times_1750_plus_layer_count_times_4500(BLUE) == 133550

    def test_gray_returns_135300(self):
        assert xcf_file_size_mod_457_times_725_plus_image_type_times_1750_plus_layer_count_times_4500(GRAY) == 135300

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_457_times_725_plus_image_type_times_1750_plus_layer_count_times_4500(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_457_times_725_plus_image_type_times_1750_plus_layer_count_times_4500(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_457_times_725_plus_image_type_times_1750_plus_layer_count_times_4500(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_457_times_725_plus_image_type_times_1750_plus_layer_count_times_4500(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_457_times_725_plus_image_type_times_1750_plus_layer_count_times_4500(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_457_times_725_plus_image_type_times_1750_plus_layer_count_times_4500(GRAY) >
                xcf_file_size_mod_457_times_725_plus_image_type_times_1750_plus_layer_count_times_4500(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_457_times_725_plus_image_type_times_1750_plus_layer_count_times_4500(str(RED)) == 132825
