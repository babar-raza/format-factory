"""Sprint 387 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_563_times_975_plus_image_type_times_5300_plus_width_times_height_times_4600,
    xcf_file_size_mod_569_times_925_plus_image_type_times_2150_plus_layer_count_times_5300,
)


# --- F1: xcf_file_size_mod_563_times_975_plus_image_type_times_5300_plus_width_times_height_times_4600 ---

class TestXcfFileSizeMod563Times975PlusImageType5300PlusWidthHeight4600:
    def test_red_returns_177175(self):
        assert xcf_file_size_mod_563_times_975_plus_image_type_times_5300_plus_width_times_height_times_4600(RED) == 177175

    def test_blue_returns_178150(self):
        assert xcf_file_size_mod_563_times_975_plus_image_type_times_5300_plus_width_times_height_times_4600(BLUE) == 178150

    def test_gray_returns_197250(self):
        assert xcf_file_size_mod_563_times_975_plus_image_type_times_5300_plus_width_times_height_times_4600(GRAY) == 197250

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_563_times_975_plus_image_type_times_5300_plus_width_times_height_times_4600(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_563_times_975_plus_image_type_times_5300_plus_width_times_height_times_4600(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_563_times_975_plus_image_type_times_5300_plus_width_times_height_times_4600(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_563_times_975_plus_image_type_times_5300_plus_width_times_height_times_4600(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_563_times_975_plus_image_type_times_5300_plus_width_times_height_times_4600(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_563_times_975_plus_image_type_times_5300_plus_width_times_height_times_4600(GRAY) >
                xcf_file_size_mod_563_times_975_plus_image_type_times_5300_plus_width_times_height_times_4600(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_563_times_975_plus_image_type_times_5300_plus_width_times_height_times_4600(str(RED)) == 177175


# --- F2: xcf_file_size_mod_569_times_925_plus_image_type_times_2150_plus_layer_count_times_5300 ---

class TestXcfFileSizeMod569Times925PlusImageType2150PlusLayerCount5300:
    def test_red_returns_169025(self):
        assert xcf_file_size_mod_569_times_925_plus_image_type_times_2150_plus_layer_count_times_5300(RED) == 169025

    def test_blue_returns_169950(self):
        assert xcf_file_size_mod_569_times_925_plus_image_type_times_2150_plus_layer_count_times_5300(BLUE) == 169950

    def test_gray_returns_172100(self):
        assert xcf_file_size_mod_569_times_925_plus_image_type_times_2150_plus_layer_count_times_5300(GRAY) == 172100

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_569_times_925_plus_image_type_times_2150_plus_layer_count_times_5300(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_569_times_925_plus_image_type_times_2150_plus_layer_count_times_5300(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_569_times_925_plus_image_type_times_2150_plus_layer_count_times_5300(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_569_times_925_plus_image_type_times_2150_plus_layer_count_times_5300(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_569_times_925_plus_image_type_times_2150_plus_layer_count_times_5300(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_569_times_925_plus_image_type_times_2150_plus_layer_count_times_5300(GRAY) >
                xcf_file_size_mod_569_times_925_plus_image_type_times_2150_plus_layer_count_times_5300(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_569_times_925_plus_image_type_times_2150_plus_layer_count_times_5300(str(RED)) == 169025
