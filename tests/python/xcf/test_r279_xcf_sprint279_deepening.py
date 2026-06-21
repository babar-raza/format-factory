"""Sprint 279 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_23_times_250_plus_image_type_times_1300_plus_width_times_height_times_900,
    xcf_file_size_mod_19_times_100_plus_image_type_times_600_plus_layer_count_times_1400,
)


# --- F1: xcf_file_size_mod_23_times_250_plus_image_type_times_1300_plus_width_times_height_times_900 ---

class TestXcfFileSizeMod23Times250PlusImageType1300PlusWidthTimesHeight900:
    def test_red_returns_4900(self):
        assert xcf_file_size_mod_23_times_250_plus_image_type_times_1300_plus_width_times_height_times_900(RED) == 4900

    def test_blue_returns_5150(self):
        assert xcf_file_size_mod_23_times_250_plus_image_type_times_1300_plus_width_times_height_times_900(BLUE) == 5150

    def test_gray_returns_9150(self):
        assert xcf_file_size_mod_23_times_250_plus_image_type_times_1300_plus_width_times_height_times_900(GRAY) == 9150

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_23_times_250_plus_image_type_times_1300_plus_width_times_height_times_900(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_23_times_250_plus_image_type_times_1300_plus_width_times_height_times_900(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_23_times_250_plus_image_type_times_1300_plus_width_times_height_times_900(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_23_times_250_plus_image_type_times_1300_plus_width_times_height_times_900(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_23_times_250_plus_image_type_times_1300_plus_width_times_height_times_900(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_23_times_250_plus_image_type_times_1300_plus_width_times_height_times_900(GRAY) >
                xcf_file_size_mod_23_times_250_plus_image_type_times_1300_plus_width_times_height_times_900(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_23_times_250_plus_image_type_times_1300_plus_width_times_height_times_900(str(RED)) == 4900


# --- F2: xcf_file_size_mod_19_times_100_plus_image_type_times_600_plus_layer_count_times_1400 ---

class TestXcfFileSizeMod19Times100PlusImageType600PlusLayerCount1400:
    def test_red_returns_2000(self):
        assert xcf_file_size_mod_19_times_100_plus_image_type_times_600_plus_layer_count_times_1400(RED) == 2000

    def test_blue_returns_2100(self):
        assert xcf_file_size_mod_19_times_100_plus_image_type_times_600_plus_layer_count_times_1400(BLUE) == 2100

    def test_gray_returns_2700(self):
        assert xcf_file_size_mod_19_times_100_plus_image_type_times_600_plus_layer_count_times_1400(GRAY) == 2700

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_19_times_100_plus_image_type_times_600_plus_layer_count_times_1400(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_19_times_100_plus_image_type_times_600_plus_layer_count_times_1400(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_19_times_100_plus_image_type_times_600_plus_layer_count_times_1400(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_19_times_100_plus_image_type_times_600_plus_layer_count_times_1400(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_19_times_100_plus_image_type_times_600_plus_layer_count_times_1400(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_19_times_100_plus_image_type_times_600_plus_layer_count_times_1400(GRAY) >
                xcf_file_size_mod_19_times_100_plus_image_type_times_600_plus_layer_count_times_1400(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_19_times_100_plus_image_type_times_600_plus_layer_count_times_1400(str(RED)) == 2000
