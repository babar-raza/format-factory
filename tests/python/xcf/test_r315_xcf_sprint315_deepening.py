"""Sprint 315 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_257_times_375_plus_image_type_times_2900_plus_width_times_height_times_2200,
    xcf_file_size_mod_263_times_325_plus_image_type_times_950_plus_layer_count_times_2900,
)


# --- F1: xcf_file_size_mod_257_times_375_plus_image_type_times_2900_plus_width_times_height_times_2200 ---

class TestXcfFileSizeMod257Times375PlusImageType2900PlusWidthHeight2200:
    def test_red_returns_68575(self):
        assert xcf_file_size_mod_257_times_375_plus_image_type_times_2900_plus_width_times_height_times_2200(RED) == 68575

    def test_blue_returns_68950(self):
        assert xcf_file_size_mod_257_times_375_plus_image_type_times_2900_plus_width_times_height_times_2200(BLUE) == 68950

    def test_gray_returns_78450(self):
        assert xcf_file_size_mod_257_times_375_plus_image_type_times_2900_plus_width_times_height_times_2200(GRAY) == 78450

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_257_times_375_plus_image_type_times_2900_plus_width_times_height_times_2200(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_257_times_375_plus_image_type_times_2900_plus_width_times_height_times_2200(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_257_times_375_plus_image_type_times_2900_plus_width_times_height_times_2200(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_257_times_375_plus_image_type_times_2900_plus_width_times_height_times_2200(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_257_times_375_plus_image_type_times_2900_plus_width_times_height_times_2200(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_257_times_375_plus_image_type_times_2900_plus_width_times_height_times_2200(GRAY) >
                xcf_file_size_mod_257_times_375_plus_image_type_times_2900_plus_width_times_height_times_2200(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_257_times_375_plus_image_type_times_2900_plus_width_times_height_times_2200(str(RED)) == 68575


# --- F2: xcf_file_size_mod_263_times_325_plus_image_type_times_950_plus_layer_count_times_2900 ---

class TestXcfFileSizeMod263Times325PlusImageType950PlusLayerCount2900:
    def test_red_returns_60425(self):
        assert xcf_file_size_mod_263_times_325_plus_image_type_times_950_plus_layer_count_times_2900(RED) == 60425

    def test_blue_returns_60750(self):
        assert xcf_file_size_mod_263_times_325_plus_image_type_times_950_plus_layer_count_times_2900(BLUE) == 60750

    def test_gray_returns_61700(self):
        assert xcf_file_size_mod_263_times_325_plus_image_type_times_950_plus_layer_count_times_2900(GRAY) == 61700

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_263_times_325_plus_image_type_times_950_plus_layer_count_times_2900(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_263_times_325_plus_image_type_times_950_plus_layer_count_times_2900(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_263_times_325_plus_image_type_times_950_plus_layer_count_times_2900(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_263_times_325_plus_image_type_times_950_plus_layer_count_times_2900(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_263_times_325_plus_image_type_times_950_plus_layer_count_times_2900(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_263_times_325_plus_image_type_times_950_plus_layer_count_times_2900(GRAY) >
                xcf_file_size_mod_263_times_325_plus_image_type_times_950_plus_layer_count_times_2900(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_263_times_325_plus_image_type_times_950_plus_layer_count_times_2900(str(RED)) == 60425
