"""Sprint 447 XCF analytics deepening tests."""
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"
RED = _XCF / "1x1-red-rgb.xcf"
BLUE = _XCF / "1x1-rgba-blue.xcf"
GRAY = _XCF / "2x2-gray.xcf"

from src.python.xcf.xcf_parser import (
    xcf_file_size_mod_823_times_1550_plus_image_type_times_7600_plus_width_times_height_times_6600,
    xcf_file_size_mod_827_times_1500_plus_image_type_times_3300_plus_layer_count_times_7600,
)


class TestXcfFileSizeMod823Times1550PlusImageType7600PlusWidthHeight6600:
    def test_red_returns_280950(self):
        assert xcf_file_size_mod_823_times_1550_plus_image_type_times_7600_plus_width_times_height_times_6600(RED) == 280950

    def test_blue_returns_282500(self):
        assert xcf_file_size_mod_823_times_1550_plus_image_type_times_7600_plus_width_times_height_times_6600(BLUE) == 282500

    def test_gray_returns_309900(self):
        assert xcf_file_size_mod_823_times_1550_plus_image_type_times_7600_plus_width_times_height_times_6600(GRAY) == 309900

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_823_times_1550_plus_image_type_times_7600_plus_width_times_height_times_6600(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_823_times_1550_plus_image_type_times_7600_plus_width_times_height_times_6600(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_823_times_1550_plus_image_type_times_7600_plus_width_times_height_times_6600(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_823_times_1550_plus_image_type_times_7600_plus_width_times_height_times_6600(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_823_times_1550_plus_image_type_times_7600_plus_width_times_height_times_6600(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_823_times_1550_plus_image_type_times_7600_plus_width_times_height_times_6600(GRAY) >
                xcf_file_size_mod_823_times_1550_plus_image_type_times_7600_plus_width_times_height_times_6600(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_823_times_1550_plus_image_type_times_7600_plus_width_times_height_times_6600(str(RED)) == 280950


class TestXcfFileSizeMod827Times1500PlusImageType3300PlusLayerCount7600:
    def test_red_returns_273100(self):
        assert xcf_file_size_mod_827_times_1500_plus_image_type_times_3300_plus_layer_count_times_7600(RED) == 273100

    def test_blue_returns_274600(self):
        assert xcf_file_size_mod_827_times_1500_plus_image_type_times_3300_plus_layer_count_times_7600(BLUE) == 274600

    def test_gray_returns_277900(self):
        assert xcf_file_size_mod_827_times_1500_plus_image_type_times_3300_plus_layer_count_times_7600(GRAY) == 277900

    def test_red_returns_int(self):
        assert isinstance(xcf_file_size_mod_827_times_1500_plus_image_type_times_3300_plus_layer_count_times_7600(RED), int)

    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_827_times_1500_plus_image_type_times_3300_plus_layer_count_times_7600(BLUE), int)

    def test_gray_returns_int(self):
        assert isinstance(xcf_file_size_mod_827_times_1500_plus_image_type_times_3300_plus_layer_count_times_7600(GRAY), int)

    def test_red_nonnegative(self):
        assert xcf_file_size_mod_827_times_1500_plus_image_type_times_3300_plus_layer_count_times_7600(RED) >= 0

    def test_blue_nonnegative(self):
        assert xcf_file_size_mod_827_times_1500_plus_image_type_times_3300_plus_layer_count_times_7600(BLUE) >= 0

    def test_gray_greater_than_red(self):
        assert (xcf_file_size_mod_827_times_1500_plus_image_type_times_3300_plus_layer_count_times_7600(GRAY) >
                xcf_file_size_mod_827_times_1500_plus_image_type_times_3300_plus_layer_count_times_7600(RED))

    def test_accepts_string_path(self):
        assert xcf_file_size_mod_827_times_1500_plus_image_type_times_3300_plus_layer_count_times_7600(str(RED)) == 273100
