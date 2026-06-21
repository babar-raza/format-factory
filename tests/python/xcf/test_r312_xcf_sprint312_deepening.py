"""Sprint 312 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_233_times_350_plus_image_type_times_2800_plus_width_times_height_times_2100,
    xcf_file_size_mod_239_times_300_plus_image_type_times_900_plus_layer_count_times_2800,
)


# --- F1: xcf_file_size_mod_233_times_350_plus_image_type_times_2800_plus_width_times_height_times_2100 ---

class TestXcfFileSizeMod233Times350PlusImageType2800PlusWidthTimesHeight2100:
    def test_red_returns_64050(self):
        assert xcf_file_size_mod_233_times_350_plus_image_type_times_2800_plus_width_times_height_times_2100(RED) == 64050

    def test_blue_returns_64400(self):
        assert xcf_file_size_mod_233_times_350_plus_image_type_times_2800_plus_width_times_height_times_2100(BLUE) == 64400

    def test_gray_returns_73500(self):
        assert xcf_file_size_mod_233_times_350_plus_image_type_times_2800_plus_width_times_height_times_2100(GRAY) == 73500

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_233_times_350_plus_image_type_times_2800_plus_width_times_height_times_2100(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_233_times_350_plus_image_type_times_2800_plus_width_times_height_times_2100(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_233_times_350_plus_image_type_times_2800_plus_width_times_height_times_2100(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_233_times_350_plus_image_type_times_2800_plus_width_times_height_times_2100(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_233_times_350_plus_image_type_times_2800_plus_width_times_height_times_2100(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_233_times_350_plus_image_type_times_2800_plus_width_times_height_times_2100(GRAY) >
                xcf_file_size_mod_233_times_350_plus_image_type_times_2800_plus_width_times_height_times_2100(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_233_times_350_plus_image_type_times_2800_plus_width_times_height_times_2100(str(RED)) == 64050


# --- F2: xcf_file_size_mod_239_times_300_plus_image_type_times_900_plus_layer_count_times_2800 ---

class TestXcfFileSizeMod239Times300PlusImageType900PlusLayerCount2800:
    def test_red_returns_55900(self):
        assert xcf_file_size_mod_239_times_300_plus_image_type_times_900_plus_layer_count_times_2800(RED) == 55900

    def test_blue_returns_56200(self):
        assert xcf_file_size_mod_239_times_300_plus_image_type_times_900_plus_layer_count_times_2800(BLUE) == 56200

    def test_gray_returns_57100(self):
        assert xcf_file_size_mod_239_times_300_plus_image_type_times_900_plus_layer_count_times_2800(GRAY) == 57100

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_239_times_300_plus_image_type_times_900_plus_layer_count_times_2800(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_239_times_300_plus_image_type_times_900_plus_layer_count_times_2800(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_239_times_300_plus_image_type_times_900_plus_layer_count_times_2800(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_239_times_300_plus_image_type_times_900_plus_layer_count_times_2800(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_239_times_300_plus_image_type_times_900_plus_layer_count_times_2800(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_239_times_300_plus_image_type_times_900_plus_layer_count_times_2800(GRAY) >
                xcf_file_size_mod_239_times_300_plus_image_type_times_900_plus_layer_count_times_2800(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_239_times_300_plus_image_type_times_900_plus_layer_count_times_2800(str(RED)) == 55900
