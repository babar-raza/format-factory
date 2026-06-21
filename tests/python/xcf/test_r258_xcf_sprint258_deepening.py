"""Sprint 258 XCF analytics deepening tests.

Samples: 1x1-red-rgb.xcf (fs=177, type=0, w=1, h=1)
         1x1-rgba-blue.xcf (fs=178, type=0, w=1, h=1)
         2x2-gray.xcf (fs=178, type=1, w=2, h=2)

F1: xcf_file_size_mod_19_times_100_plus_image_type_times_1200_plus_width_times_height_times_400
    RED=1000, BLUE=1100, GRAY=3500
F2: xcf_file_size_mod_13_times_300_plus_image_type_times_800_plus_width_plus_height_times_200
    RED=2800, BLUE=3100, GRAY=4300
"""
from pathlib import Path

from src.python.xcf import (
    xcf_file_size_mod_19_times_100_plus_image_type_times_1200_plus_width_times_height_times_400,
    xcf_file_size_mod_13_times_300_plus_image_type_times_800_plus_width_plus_height_times_200,
)

_REPO = Path(__file__).parent.parent.parent.parent
_XCF = _REPO / "samples" / "by-format" / "xcf" / "valid"

RED = str(_XCF / "1x1-red-rgb.xcf")
BLUE = str(_XCF / "1x1-rgba-blue.xcf")
GRAY = str(_XCF / "2x2-gray.xcf")


# --- F1 tests ---

class TestF1Red:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_19_times_100_plus_image_type_times_1200_plus_width_times_height_times_400(RED), int)

    def test_value(self):
        assert xcf_file_size_mod_19_times_100_plus_image_type_times_1200_plus_width_times_height_times_400(RED) == 1000

    def test_nonnegative(self):
        assert xcf_file_size_mod_19_times_100_plus_image_type_times_1200_plus_width_times_height_times_400(RED) >= 0


class TestF1Blue:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_19_times_100_plus_image_type_times_1200_plus_width_times_height_times_400(BLUE), int)

    def test_value(self):
        assert xcf_file_size_mod_19_times_100_plus_image_type_times_1200_plus_width_times_height_times_400(BLUE) == 1100

    def test_nonnegative(self):
        assert xcf_file_size_mod_19_times_100_plus_image_type_times_1200_plus_width_times_height_times_400(BLUE) >= 0


class TestF1Gray:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_19_times_100_plus_image_type_times_1200_plus_width_times_height_times_400(GRAY), int)

    def test_value(self):
        assert xcf_file_size_mod_19_times_100_plus_image_type_times_1200_plus_width_times_height_times_400(GRAY) == 3500

    def test_nonnegative(self):
        assert xcf_file_size_mod_19_times_100_plus_image_type_times_1200_plus_width_times_height_times_400(GRAY) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_19_times_100_plus_image_type_times_1200_plus_width_times_height_times_400(GRAY) >
                xcf_file_size_mod_19_times_100_plus_image_type_times_1200_plus_width_times_height_times_400(BLUE))


# --- F2 tests ---

class TestF2Red:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_13_times_300_plus_image_type_times_800_plus_width_plus_height_times_200(RED), int)

    def test_value(self):
        assert xcf_file_size_mod_13_times_300_plus_image_type_times_800_plus_width_plus_height_times_200(RED) == 2800

    def test_nonnegative(self):
        assert xcf_file_size_mod_13_times_300_plus_image_type_times_800_plus_width_plus_height_times_200(RED) >= 0


class TestF2Blue:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_13_times_300_plus_image_type_times_800_plus_width_plus_height_times_200(BLUE), int)

    def test_value(self):
        assert xcf_file_size_mod_13_times_300_plus_image_type_times_800_plus_width_plus_height_times_200(BLUE) == 3100

    def test_nonnegative(self):
        assert xcf_file_size_mod_13_times_300_plus_image_type_times_800_plus_width_plus_height_times_200(BLUE) >= 0


class TestF2Gray:
    def test_returns_int(self):
        assert isinstance(xcf_file_size_mod_13_times_300_plus_image_type_times_800_plus_width_plus_height_times_200(GRAY), int)

    def test_value(self):
        assert xcf_file_size_mod_13_times_300_plus_image_type_times_800_plus_width_plus_height_times_200(GRAY) == 4300

    def test_nonnegative(self):
        assert xcf_file_size_mod_13_times_300_plus_image_type_times_800_plus_width_plus_height_times_200(GRAY) >= 0

    def test_gray_greater_than_blue(self):
        assert (xcf_file_size_mod_13_times_300_plus_image_type_times_800_plus_width_plus_height_times_200(GRAY) >
                xcf_file_size_mod_13_times_300_plus_image_type_times_800_plus_width_plus_height_times_200(BLUE))
