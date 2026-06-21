"""Sprint 261 XCF analytics deepening tests.

F1: xcf_file_size_mod_29_times_200_plus_image_type_times_1500_plus_width_times_height_times_500
    RED=1100, BLUE=1300, GRAY=4300
F2: xcf_file_size_mod_23_times_150_plus_image_type_times_1000_plus_layer_count_times_600
    RED=3000, BLUE=3150, GRAY=4150
"""
from pathlib import Path

from src.python.xcf import (
    xcf_file_size_mod_29_times_200_plus_image_type_times_1500_plus_width_times_height_times_500,
    xcf_file_size_mod_23_times_150_plus_image_type_times_1000_plus_layer_count_times_600,
)

_REPO = Path(__file__).parent.parent.parent.parent
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"

RED = str(_XCF / "1x1-red-rgb.xcf")
BLUE = str(_XCF / "1x1-rgba-blue.xcf")
GRAY = str(_XCF / "2x2-gray.xcf")


class TestF1Red:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_29_times_200_plus_image_type_times_1500_plus_width_times_height_times_500(RED), int)

    def test_value(self):
        assert xcf_file_size_mod_29_times_200_plus_image_type_times_1500_plus_width_times_height_times_500(RED) == 1100

    def test_nonnegative(self):
        assert xcf_file_size_mod_29_times_200_plus_image_type_times_1500_plus_width_times_height_times_500(RED) >= 0


class TestF1Blue:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_29_times_200_plus_image_type_times_1500_plus_width_times_height_times_500(BLUE), int)

    def test_value(self):
        assert xcf_file_size_mod_29_times_200_plus_image_type_times_1500_plus_width_times_height_times_500(BLUE) == 1300

    def test_nonnegative(self):
        assert xcf_file_size_mod_29_times_200_plus_image_type_times_1500_plus_width_times_height_times_500(BLUE) >= 0


class TestF1Gray:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_29_times_200_plus_image_type_times_1500_plus_width_times_height_times_500(GRAY), int)

    def test_value(self):
        assert xcf_file_size_mod_29_times_200_plus_image_type_times_1500_plus_width_times_height_times_500(GRAY) == 4300

    def test_nonnegative(self):
        assert xcf_file_size_mod_29_times_200_plus_image_type_times_1500_plus_width_times_height_times_500(GRAY) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_29_times_200_plus_image_type_times_1500_plus_width_times_height_times_500(GRAY) >
                xcf_file_size_mod_29_times_200_plus_image_type_times_1500_plus_width_times_height_times_500(BLUE))


class TestF2Red:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_23_times_150_plus_image_type_times_1000_plus_layer_count_times_600(RED), int)

    def test_value(self):
        assert xcf_file_size_mod_23_times_150_plus_image_type_times_1000_plus_layer_count_times_600(RED) == 3000

    def test_nonnegative(self):
        assert xcf_file_size_mod_23_times_150_plus_image_type_times_1000_plus_layer_count_times_600(RED) >= 0


class TestF2Blue:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_23_times_150_plus_image_type_times_1000_plus_layer_count_times_600(BLUE), int)

    def test_value(self):
        assert xcf_file_size_mod_23_times_150_plus_image_type_times_1000_plus_layer_count_times_600(BLUE) == 3150

    def test_nonnegative(self):
        assert xcf_file_size_mod_23_times_150_plus_image_type_times_1000_plus_layer_count_times_600(BLUE) >= 0


class TestF2Gray:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_23_times_150_plus_image_type_times_1000_plus_layer_count_times_600(GRAY), int)

    def test_value(self):
        assert xcf_file_size_mod_23_times_150_plus_image_type_times_1000_plus_layer_count_times_600(GRAY) == 4150

    def test_nonnegative(self):
        assert xcf_file_size_mod_23_times_150_plus_image_type_times_1000_plus_layer_count_times_600(GRAY) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_23_times_150_plus_image_type_times_1000_plus_layer_count_times_600(GRAY) >
                xcf_file_size_mod_23_times_150_plus_image_type_times_1000_plus_layer_count_times_600(BLUE))
