"""Sprint 306 XCF analytics deepening tests."""
from pathlib import Path
import pytest

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_197_times_300_plus_image_type_times_2600_plus_width_times_height_times_1900,
    xcf_file_size_mod_199_times_250_plus_image_type_times_800_plus_layer_count_times_2600,
)


# --- F1: xcf_file_size_mod_197_times_300_plus_image_type_times_2600_plus_width_times_height_times_1900 ---

class TestXcfFileSizeMod197Times300PlusImageType2600PlusWidthTimesHeight1900:
    def test_red_returns_55000(self):
        assert xcf_file_size_mod_197_times_300_plus_image_type_times_2600_plus_width_times_height_times_1900(RED) == 55000

    def test_blue_returns_55300(self):
        assert xcf_file_size_mod_197_times_300_plus_image_type_times_2600_plus_width_times_height_times_1900(BLUE) == 55300

    def test_gray_returns_63600(self):
        assert xcf_file_size_mod_197_times_300_plus_image_type_times_2600_plus_width_times_height_times_1900(GRAY) == 63600

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_197_times_300_plus_image_type_times_2600_plus_width_times_height_times_1900(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_197_times_300_plus_image_type_times_2600_plus_width_times_height_times_1900(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_197_times_300_plus_image_type_times_2600_plus_width_times_height_times_1900(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_197_times_300_plus_image_type_times_2600_plus_width_times_height_times_1900(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_197_times_300_plus_image_type_times_2600_plus_width_times_height_times_1900(BLUE) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_197_times_300_plus_image_type_times_2600_plus_width_times_height_times_1900(GRAY) >
                xcf_file_size_mod_197_times_300_plus_image_type_times_2600_plus_width_times_height_times_1900(BLUE))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_197_times_300_plus_image_type_times_2600_plus_width_times_height_times_1900(str(RED)) == 55000


# --- F2: xcf_file_size_mod_199_times_250_plus_image_type_times_800_plus_layer_count_times_2600 ---

class TestXcfFileSizeMod199Times250PlusImageType800PlusLayerCount2600:
    def test_red_returns_46850(self):
        assert xcf_file_size_mod_199_times_250_plus_image_type_times_800_plus_layer_count_times_2600(RED) == 46850

    def test_blue_returns_47100(self):
        assert xcf_file_size_mod_199_times_250_plus_image_type_times_800_plus_layer_count_times_2600(BLUE) == 47100

    def test_gray_returns_47900(self):
        assert xcf_file_size_mod_199_times_250_plus_image_type_times_800_plus_layer_count_times_2600(GRAY) == 47900

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_199_times_250_plus_image_type_times_800_plus_layer_count_times_2600(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_199_times_250_plus_image_type_times_800_plus_layer_count_times_2600(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_199_times_250_plus_image_type_times_800_plus_layer_count_times_2600(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_199_times_250_plus_image_type_times_800_plus_layer_count_times_2600(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_199_times_250_plus_image_type_times_800_plus_layer_count_times_2600(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_199_times_250_plus_image_type_times_800_plus_layer_count_times_2600(GRAY) >
                xcf_file_size_mod_199_times_250_plus_image_type_times_800_plus_layer_count_times_2600(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_199_times_250_plus_image_type_times_800_plus_layer_count_times_2600(str(RED)) == 46850
