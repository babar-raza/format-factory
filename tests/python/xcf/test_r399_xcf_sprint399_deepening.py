"""Sprint 399 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_607_times_1075_plus_image_type_times_5700_plus_width_times_height_times_5000,
    xcf_file_size_mod_613_times_1025_plus_image_type_times_2350_plus_layer_count_times_5700,
)


# --- F1: xcf_file_size_mod_607_times_1075_plus_image_type_times_5700_plus_width_times_height_times_5000 ---

class TestXcfFileSizeMod607Times1075PlusImageType5700PlusWidthHeight5000:
    def test_red_returns_195275(self):
        assert xcf_file_size_mod_607_times_1075_plus_image_type_times_5700_plus_width_times_height_times_5000(RED) == 195275

    def test_blue_returns_196350(self):
        assert xcf_file_size_mod_607_times_1075_plus_image_type_times_5700_plus_width_times_height_times_5000(BLUE) == 196350

    def test_gray_returns_217050(self):
        assert xcf_file_size_mod_607_times_1075_plus_image_type_times_5700_plus_width_times_height_times_5000(GRAY) == 217050

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_607_times_1075_plus_image_type_times_5700_plus_width_times_height_times_5000(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_607_times_1075_plus_image_type_times_5700_plus_width_times_height_times_5000(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_607_times_1075_plus_image_type_times_5700_plus_width_times_height_times_5000(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_607_times_1075_plus_image_type_times_5700_plus_width_times_height_times_5000(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_607_times_1075_plus_image_type_times_5700_plus_width_times_height_times_5000(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_607_times_1075_plus_image_type_times_5700_plus_width_times_height_times_5000(GRAY) >
                xcf_file_size_mod_607_times_1075_plus_image_type_times_5700_plus_width_times_height_times_5000(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_607_times_1075_plus_image_type_times_5700_plus_width_times_height_times_5000(str(RED)) == 195275


# --- F2: xcf_file_size_mod_613_times_1025_plus_image_type_times_2350_plus_layer_count_times_5700 ---

class TestXcfFileSizeMod613Times1025PlusImageType2350PlusLayerCount5700:
    def test_red_returns_187125(self):
        assert xcf_file_size_mod_613_times_1025_plus_image_type_times_2350_plus_layer_count_times_5700(RED) == 187125

    def test_blue_returns_188150(self):
        assert xcf_file_size_mod_613_times_1025_plus_image_type_times_2350_plus_layer_count_times_5700(BLUE) == 188150

    def test_gray_returns_190500(self):
        assert xcf_file_size_mod_613_times_1025_plus_image_type_times_2350_plus_layer_count_times_5700(GRAY) == 190500

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_613_times_1025_plus_image_type_times_2350_plus_layer_count_times_5700(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_613_times_1025_plus_image_type_times_2350_plus_layer_count_times_5700(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_613_times_1025_plus_image_type_times_2350_plus_layer_count_times_5700(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_613_times_1025_plus_image_type_times_2350_plus_layer_count_times_5700(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_613_times_1025_plus_image_type_times_2350_plus_layer_count_times_5700(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_613_times_1025_plus_image_type_times_2350_plus_layer_count_times_5700(GRAY) >
                xcf_file_size_mod_613_times_1025_plus_image_type_times_2350_plus_layer_count_times_5700(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_613_times_1025_plus_image_type_times_2350_plus_layer_count_times_5700(str(RED)) == 187125
