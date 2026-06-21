"""Sprint 339 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_353_times_575_plus_image_type_times_3700_plus_width_times_height_times_3000,
    xcf_file_size_mod_359_times_525_plus_image_type_times_1350_plus_layer_count_times_3700,
)


# --- F1: xcf_file_size_mod_353_times_575_plus_image_type_times_3700_plus_width_times_height_times_3000 ---

class TestXcfFileSizeMod353Times575PlusImageType3700PlusWidthHeight3000:
    def test_red_returns_104775(self):
        assert xcf_file_size_mod_353_times_575_plus_image_type_times_3700_plus_width_times_height_times_3000(RED) == 104775

    def test_blue_returns_105350(self):
        assert xcf_file_size_mod_353_times_575_plus_image_type_times_3700_plus_width_times_height_times_3000(BLUE) == 105350

    def test_gray_returns_118050(self):
        assert xcf_file_size_mod_353_times_575_plus_image_type_times_3700_plus_width_times_height_times_3000(GRAY) == 118050

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_353_times_575_plus_image_type_times_3700_plus_width_times_height_times_3000(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_353_times_575_plus_image_type_times_3700_plus_width_times_height_times_3000(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_353_times_575_plus_image_type_times_3700_plus_width_times_height_times_3000(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_353_times_575_plus_image_type_times_3700_plus_width_times_height_times_3000(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_353_times_575_plus_image_type_times_3700_plus_width_times_height_times_3000(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_353_times_575_plus_image_type_times_3700_plus_width_times_height_times_3000(GRAY) >
                xcf_file_size_mod_353_times_575_plus_image_type_times_3700_plus_width_times_height_times_3000(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_353_times_575_plus_image_type_times_3700_plus_width_times_height_times_3000(str(RED)) == 104775


# --- F2: xcf_file_size_mod_359_times_525_plus_image_type_times_1350_plus_layer_count_times_3700 ---

class TestXcfFileSizeMod359Times525PlusImageType1350PlusLayerCount3700:
    def test_red_returns_96625(self):
        assert xcf_file_size_mod_359_times_525_plus_image_type_times_1350_plus_layer_count_times_3700(RED) == 96625

    def test_blue_returns_97150(self):
        assert xcf_file_size_mod_359_times_525_plus_image_type_times_1350_plus_layer_count_times_3700(BLUE) == 97150

    def test_gray_returns_98500(self):
        assert xcf_file_size_mod_359_times_525_plus_image_type_times_1350_plus_layer_count_times_3700(GRAY) == 98500

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_359_times_525_plus_image_type_times_1350_plus_layer_count_times_3700(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_359_times_525_plus_image_type_times_1350_plus_layer_count_times_3700(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_359_times_525_plus_image_type_times_1350_plus_layer_count_times_3700(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_359_times_525_plus_image_type_times_1350_plus_layer_count_times_3700(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_359_times_525_plus_image_type_times_1350_plus_layer_count_times_3700(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_359_times_525_plus_image_type_times_1350_plus_layer_count_times_3700(GRAY) >
                xcf_file_size_mod_359_times_525_plus_image_type_times_1350_plus_layer_count_times_3700(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_359_times_525_plus_image_type_times_1350_plus_layer_count_times_3700(str(RED)) == 96625
