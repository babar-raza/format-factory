"""Sprint 441 XCF analytics deepening tests."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_797_times_1450_plus_image_type_times_7200_plus_width_times_height_times_6400,
    xcf_file_size_mod_809_times_1400_plus_image_type_times_3100_plus_layer_count_times_7200,
)


class TestXcfFileSizeMod797Times1450PlusImageType7200PlusWidthHeight6400:
    def test_red_returns_263050(self):
        assert xcf_file_size_mod_797_times_1450_plus_image_type_times_7200_plus_width_times_height_times_6400(RED) == 263050

    def test_blue_returns_264500(self):
        assert xcf_file_size_mod_797_times_1450_plus_image_type_times_7200_plus_width_times_height_times_6400(BLUE) == 264500

    def test_gray_returns_290900(self):
        assert xcf_file_size_mod_797_times_1450_plus_image_type_times_7200_plus_width_times_height_times_6400(GRAY) == 290900

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_797_times_1450_plus_image_type_times_7200_plus_width_times_height_times_6400(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_797_times_1450_plus_image_type_times_7200_plus_width_times_height_times_6400(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_797_times_1450_plus_image_type_times_7200_plus_width_times_height_times_6400(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_797_times_1450_plus_image_type_times_7200_plus_width_times_height_times_6400(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_797_times_1450_plus_image_type_times_7200_plus_width_times_height_times_6400(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_797_times_1450_plus_image_type_times_7200_plus_width_times_height_times_6400(GRAY) >
                xcf_file_size_mod_797_times_1450_plus_image_type_times_7200_plus_width_times_height_times_6400(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_797_times_1450_plus_image_type_times_7200_plus_width_times_height_times_6400(str(RED)) == 263050


class TestXcfFileSizeMod809Times1400PlusImageType3100PlusLayerCount7200:
    def test_red_returns_255000(self):
        assert xcf_file_size_mod_809_times_1400_plus_image_type_times_3100_plus_layer_count_times_7200(RED) == 255000

    def test_blue_returns_256400(self):
        assert xcf_file_size_mod_809_times_1400_plus_image_type_times_3100_plus_layer_count_times_7200(BLUE) == 256400

    def test_gray_returns_259500(self):
        assert xcf_file_size_mod_809_times_1400_plus_image_type_times_3100_plus_layer_count_times_7200(GRAY) == 259500

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_809_times_1400_plus_image_type_times_3100_plus_layer_count_times_7200(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_809_times_1400_plus_image_type_times_3100_plus_layer_count_times_7200(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_809_times_1400_plus_image_type_times_3100_plus_layer_count_times_7200(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_809_times_1400_plus_image_type_times_3100_plus_layer_count_times_7200(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_809_times_1400_plus_image_type_times_3100_plus_layer_count_times_7200(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_809_times_1400_plus_image_type_times_3100_plus_layer_count_times_7200(GRAY) >
                xcf_file_size_mod_809_times_1400_plus_image_type_times_3100_plus_layer_count_times_7200(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_809_times_1400_plus_image_type_times_3100_plus_layer_count_times_7200(str(RED)) == 255000
