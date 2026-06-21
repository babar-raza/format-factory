"""Sprint 294 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_137_times_300_plus_image_type_times_2100_plus_width_times_height_times_1400,
    xcf_file_size_mod_139_times_150_plus_image_type_times_550_plus_layer_count_times_2100,
)


# --- F1: xcf_file_size_mod_137_times_300_plus_image_type_times_2100_plus_width_times_height_times_1400 ---

class TestXcfFileSizeMod137Times300PlusImageType2100PlusWidthTimesHeight1400:
    def test_red_returns_13400(self):
        assert xcf_file_size_mod_137_times_300_plus_image_type_times_2100_plus_width_times_height_times_1400(RED) == 13400

    def test_blue_returns_13700(self):
        assert xcf_file_size_mod_137_times_300_plus_image_type_times_2100_plus_width_times_height_times_1400(BLUE) == 13700

    def test_gray_returns_20000(self):
        assert xcf_file_size_mod_137_times_300_plus_image_type_times_2100_plus_width_times_height_times_1400(GRAY) == 20000

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_137_times_300_plus_image_type_times_2100_plus_width_times_height_times_1400(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_137_times_300_plus_image_type_times_2100_plus_width_times_height_times_1400(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_137_times_300_plus_image_type_times_2100_plus_width_times_height_times_1400(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_137_times_300_plus_image_type_times_2100_plus_width_times_height_times_1400(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_137_times_300_plus_image_type_times_2100_plus_width_times_height_times_1400(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_137_times_300_plus_image_type_times_2100_plus_width_times_height_times_1400(GRAY) >
                xcf_file_size_mod_137_times_300_plus_image_type_times_2100_plus_width_times_height_times_1400(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_137_times_300_plus_image_type_times_2100_plus_width_times_height_times_1400(str(RED)) == 13400


# --- F2: xcf_file_size_mod_139_times_150_plus_image_type_times_550_plus_layer_count_times_2100 ---

class TestXcfFileSizeMod139Times150PlusImageType550PlusLayerCount2100:
    def test_red_returns_7800(self):
        assert xcf_file_size_mod_139_times_150_plus_image_type_times_550_plus_layer_count_times_2100(RED) == 7800

    def test_blue_returns_7950(self):
        assert xcf_file_size_mod_139_times_150_plus_image_type_times_550_plus_layer_count_times_2100(BLUE) == 7950

    def test_gray_returns_8500(self):
        assert xcf_file_size_mod_139_times_150_plus_image_type_times_550_plus_layer_count_times_2100(GRAY) == 8500

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_139_times_150_plus_image_type_times_550_plus_layer_count_times_2100(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_139_times_150_plus_image_type_times_550_plus_layer_count_times_2100(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_139_times_150_plus_image_type_times_550_plus_layer_count_times_2100(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_139_times_150_plus_image_type_times_550_plus_layer_count_times_2100(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_139_times_150_plus_image_type_times_550_plus_layer_count_times_2100(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_139_times_150_plus_image_type_times_550_plus_layer_count_times_2100(GRAY) >
                xcf_file_size_mod_139_times_150_plus_image_type_times_550_plus_layer_count_times_2100(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_139_times_150_plus_image_type_times_550_plus_layer_count_times_2100(str(RED)) == 7800
