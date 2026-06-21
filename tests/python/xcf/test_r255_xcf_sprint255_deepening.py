"""Sprint 255 XCF analytics deepening tests.

Samples: 1x1-red-rgb.xcf (fs=177, type=0, w=1, h=1, lc=1)
         1x1-rgba-blue.xcf (fs=178, type=0, w=1, h=1, lc=1)
         2x2-gray.xcf (fs=178, type=1, w=2, h=2, lc=1)

F1: xcf_file_size_mod_17_times_100_plus_image_type_times_1100_plus_width_times_height_times_250
    RED=950, BLUE=1050, GRAY=2900
F2: xcf_file_size_mod_11_times_200_plus_image_type_times_700_plus_layer_count_times_500
    RED=700, BLUE=900, GRAY=1600
"""
from pathlib import Path

from src.python.xcf import (
    xcf_file_size_mod_17_times_100_plus_image_type_times_1100_plus_width_times_height_times_250,
    xcf_file_size_mod_11_times_200_plus_image_type_times_700_plus_layer_count_times_500,
)

_REPO = Path(__file__).parent.parent.parent.parent
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"

RED = str(_XCF / "1x1-red-rgb.xcf")
BLUE = str(_XCF / "1x1-rgba-blue.xcf")
GRAY = str(_XCF / "2x2-gray.xcf")


# --- F1 tests ---

class TestF1Red:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_17_times_100_plus_image_type_times_1100_plus_width_times_height_times_250(RED), int)

    def test_value(self):
        assert xcf_file_size_mod_17_times_100_plus_image_type_times_1100_plus_width_times_height_times_250(RED) == 950

    def test_nonnegative(self):
        assert xcf_file_size_mod_17_times_100_plus_image_type_times_1100_plus_width_times_height_times_250(RED) >= 0


class TestF1Blue:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_17_times_100_plus_image_type_times_1100_plus_width_times_height_times_250(BLUE), int)

    def test_value(self):
        assert xcf_file_size_mod_17_times_100_plus_image_type_times_1100_plus_width_times_height_times_250(BLUE) == 1050

    def test_nonnegative(self):
        assert xcf_file_size_mod_17_times_100_plus_image_type_times_1100_plus_width_times_height_times_250(BLUE) >= 0


class TestF1Gray:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_17_times_100_plus_image_type_times_1100_plus_width_times_height_times_250(GRAY), int)

    def test_value(self):
        assert xcf_file_size_mod_17_times_100_plus_image_type_times_1100_plus_width_times_height_times_250(GRAY) == 2900

    def test_nonnegative(self):
        assert xcf_file_size_mod_17_times_100_plus_image_type_times_1100_plus_width_times_height_times_250(GRAY) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_17_times_100_plus_image_type_times_1100_plus_width_times_height_times_250(GRAY) >
                xcf_file_size_mod_17_times_100_plus_image_type_times_1100_plus_width_times_height_times_250(BLUE))


# --- F2 tests ---

class TestF2Red:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_11_times_200_plus_image_type_times_700_plus_layer_count_times_500(RED), int)

    def test_value(self):
        assert xcf_file_size_mod_11_times_200_plus_image_type_times_700_plus_layer_count_times_500(RED) == 700

    def test_nonnegative(self):
        assert xcf_file_size_mod_11_times_200_plus_image_type_times_700_plus_layer_count_times_500(RED) >= 0


class TestF2Blue:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_11_times_200_plus_image_type_times_700_plus_layer_count_times_500(BLUE), int)

    def test_value(self):
        assert xcf_file_size_mod_11_times_200_plus_image_type_times_700_plus_layer_count_times_500(BLUE) == 900

    def test_nonnegative(self):
        assert xcf_file_size_mod_11_times_200_plus_image_type_times_700_plus_layer_count_times_500(BLUE) >= 0


class TestF2Gray:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_11_times_200_plus_image_type_times_700_plus_layer_count_times_500(GRAY), int)

    def test_value(self):
        assert xcf_file_size_mod_11_times_200_plus_image_type_times_700_plus_layer_count_times_500(GRAY) == 1600

    def test_nonnegative(self):
        assert xcf_file_size_mod_11_times_200_plus_image_type_times_700_plus_layer_count_times_500(GRAY) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_11_times_200_plus_image_type_times_700_plus_layer_count_times_500(GRAY) >
                xcf_file_size_mod_11_times_200_plus_image_type_times_700_plus_layer_count_times_500(BLUE))
