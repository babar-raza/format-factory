"""Sprint 435 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_761_times_1375_plus_image_type_times_6900_plus_width_times_height_times_6200,
    xcf_file_size_mod_769_times_1325_plus_image_type_times_2950_plus_layer_count_times_6900,
)


class TestXcfFileSizeMod761Times1375PlusImageType6900PlusWidthHeight6200:
    def test_red_returns_249575(self):
        assert xcf_file_size_mod_761_times_1375_plus_image_type_times_6900_plus_width_times_height_times_6200(RED) == 249575

    def test_blue_returns_250950(self):
        assert xcf_file_size_mod_761_times_1375_plus_image_type_times_6900_plus_width_times_height_times_6200(BLUE) == 250950

    def test_gray_returns_276450(self):
        assert xcf_file_size_mod_761_times_1375_plus_image_type_times_6900_plus_width_times_height_times_6200(GRAY) == 276450

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_761_times_1375_plus_image_type_times_6900_plus_width_times_height_times_6200(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_761_times_1375_plus_image_type_times_6900_plus_width_times_height_times_6200(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_761_times_1375_plus_image_type_times_6900_plus_width_times_height_times_6200(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_761_times_1375_plus_image_type_times_6900_plus_width_times_height_times_6200(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_761_times_1375_plus_image_type_times_6900_plus_width_times_height_times_6200(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_761_times_1375_plus_image_type_times_6900_plus_width_times_height_times_6200(GRAY) >
                xcf_file_size_mod_761_times_1375_plus_image_type_times_6900_plus_width_times_height_times_6200(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_761_times_1375_plus_image_type_times_6900_plus_width_times_height_times_6200(str(RED)) == 249575


class TestXcfFileSizeMod769Times1325PlusImageType2950PlusLayerCount6900:
    def test_red_returns_241425(self):
        assert xcf_file_size_mod_769_times_1325_plus_image_type_times_2950_plus_layer_count_times_6900(RED) == 241425

    def test_blue_returns_242750(self):
        assert xcf_file_size_mod_769_times_1325_plus_image_type_times_2950_plus_layer_count_times_6900(BLUE) == 242750

    def test_gray_returns_245700(self):
        assert xcf_file_size_mod_769_times_1325_plus_image_type_times_2950_plus_layer_count_times_6900(GRAY) == 245700

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_769_times_1325_plus_image_type_times_2950_plus_layer_count_times_6900(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_769_times_1325_plus_image_type_times_2950_plus_layer_count_times_6900(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_769_times_1325_plus_image_type_times_2950_plus_layer_count_times_6900(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_769_times_1325_plus_image_type_times_2950_plus_layer_count_times_6900(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_769_times_1325_plus_image_type_times_2950_plus_layer_count_times_6900(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_769_times_1325_plus_image_type_times_2950_plus_layer_count_times_6900(GRAY) >
                xcf_file_size_mod_769_times_1325_plus_image_type_times_2950_plus_layer_count_times_6900(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_769_times_1325_plus_image_type_times_2950_plus_layer_count_times_6900(str(RED)) == 241425
