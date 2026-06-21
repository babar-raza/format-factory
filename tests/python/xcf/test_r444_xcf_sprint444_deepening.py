"""Sprint 444 XCF analytics deepening tests."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_811_times_1500_plus_image_type_times_7400_plus_width_times_height_times_6500,
    xcf_file_size_mod_821_times_1450_plus_image_type_times_3200_plus_layer_count_times_7400,
)


class TestXcfFileSizeMod811Times1500PlusImageType7400PlusWidthHeight6500:
    def test_red_returns_272000(self):
        assert xcf_file_size_mod_811_times_1500_plus_image_type_times_7400_plus_width_times_height_times_6500(RED) == 272000

    def test_blue_returns_273500(self):
        assert xcf_file_size_mod_811_times_1500_plus_image_type_times_7400_plus_width_times_height_times_6500(BLUE) == 273500

    def test_gray_returns_300400(self):
        assert xcf_file_size_mod_811_times_1500_plus_image_type_times_7400_plus_width_times_height_times_6500(GRAY) == 300400

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_811_times_1500_plus_image_type_times_7400_plus_width_times_height_times_6500(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_811_times_1500_plus_image_type_times_7400_plus_width_times_height_times_6500(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_811_times_1500_plus_image_type_times_7400_plus_width_times_height_times_6500(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_811_times_1500_plus_image_type_times_7400_plus_width_times_height_times_6500(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_811_times_1500_plus_image_type_times_7400_plus_width_times_height_times_6500(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_811_times_1500_plus_image_type_times_7400_plus_width_times_height_times_6500(GRAY) >
                xcf_file_size_mod_811_times_1500_plus_image_type_times_7400_plus_width_times_height_times_6500(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_811_times_1500_plus_image_type_times_7400_plus_width_times_height_times_6500(str(RED)) == 272000


class TestXcfFileSizeMod821Times1450PlusImageType3200PlusLayerCount7400:
    def test_red_returns_264050(self):
        assert xcf_file_size_mod_821_times_1450_plus_image_type_times_3200_plus_layer_count_times_7400(RED) == 264050

    def test_blue_returns_265500(self):
        assert xcf_file_size_mod_821_times_1450_plus_image_type_times_3200_plus_layer_count_times_7400(BLUE) == 265500

    def test_gray_returns_268700(self):
        assert xcf_file_size_mod_821_times_1450_plus_image_type_times_3200_plus_layer_count_times_7400(GRAY) == 268700

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_821_times_1450_plus_image_type_times_3200_plus_layer_count_times_7400(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_821_times_1450_plus_image_type_times_3200_plus_layer_count_times_7400(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_821_times_1450_plus_image_type_times_3200_plus_layer_count_times_7400(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_821_times_1450_plus_image_type_times_3200_plus_layer_count_times_7400(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_821_times_1450_plus_image_type_times_3200_plus_layer_count_times_7400(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_821_times_1450_plus_image_type_times_3200_plus_layer_count_times_7400(GRAY) >
                xcf_file_size_mod_821_times_1450_plus_image_type_times_3200_plus_layer_count_times_7400(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_821_times_1450_plus_image_type_times_3200_plus_layer_count_times_7400(str(RED)) == 264050
