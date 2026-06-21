"""Sprint 426 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_727_times_1300_plus_image_type_times_6600_plus_width_times_height_times_5900,
    xcf_file_size_mod_733_times_1250_plus_image_type_times_2800_plus_layer_count_times_6600,
)


# --- F1: xcf_file_size_mod_727_times_1300_plus_image_type_times_6600_plus_width_times_height_times_5900 ---

class TestXcfFileSizeMod727Times1300PlusImageType6600PlusWidthHeight5900:
    def test_red_returns_236000(self):
        assert xcf_file_size_mod_727_times_1300_plus_image_type_times_6600_plus_width_times_height_times_5900(RED) == 236000

    def test_blue_returns_237300(self):
        assert xcf_file_size_mod_727_times_1300_plus_image_type_times_6600_plus_width_times_height_times_5900(BLUE) == 237300

    def test_gray_returns_261600(self):
        assert xcf_file_size_mod_727_times_1300_plus_image_type_times_6600_plus_width_times_height_times_5900(GRAY) == 261600

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_727_times_1300_plus_image_type_times_6600_plus_width_times_height_times_5900(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_727_times_1300_plus_image_type_times_6600_plus_width_times_height_times_5900(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_727_times_1300_plus_image_type_times_6600_plus_width_times_height_times_5900(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_727_times_1300_plus_image_type_times_6600_plus_width_times_height_times_5900(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_727_times_1300_plus_image_type_times_6600_plus_width_times_height_times_5900(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_727_times_1300_plus_image_type_times_6600_plus_width_times_height_times_5900(GRAY) >
                xcf_file_size_mod_727_times_1300_plus_image_type_times_6600_plus_width_times_height_times_5900(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_727_times_1300_plus_image_type_times_6600_plus_width_times_height_times_5900(str(RED)) == 236000


# --- F2: xcf_file_size_mod_733_times_1250_plus_image_type_times_2800_plus_layer_count_times_6600 ---

class TestXcfFileSizeMod733Times1250PlusImageType2800PlusLayerCount6600:
    def test_red_returns_227850(self):
        assert xcf_file_size_mod_733_times_1250_plus_image_type_times_2800_plus_layer_count_times_6600(RED) == 227850

    def test_blue_returns_229100(self):
        assert xcf_file_size_mod_733_times_1250_plus_image_type_times_2800_plus_layer_count_times_6600(BLUE) == 229100

    def test_gray_returns_231900(self):
        assert xcf_file_size_mod_733_times_1250_plus_image_type_times_2800_plus_layer_count_times_6600(GRAY) == 231900

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_733_times_1250_plus_image_type_times_2800_plus_layer_count_times_6600(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_733_times_1250_plus_image_type_times_2800_plus_layer_count_times_6600(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_733_times_1250_plus_image_type_times_2800_plus_layer_count_times_6600(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_733_times_1250_plus_image_type_times_2800_plus_layer_count_times_6600(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_733_times_1250_plus_image_type_times_2800_plus_layer_count_times_6600(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_733_times_1250_plus_image_type_times_2800_plus_layer_count_times_6600(GRAY) >
                xcf_file_size_mod_733_times_1250_plus_image_type_times_2800_plus_layer_count_times_6600(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_733_times_1250_plus_image_type_times_2800_plus_layer_count_times_6600(str(RED)) == 227850
