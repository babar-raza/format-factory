"""
Sprint 252 XCF deepening tests.
Functions: xcf_file_size_mod_227_times_12_plus_image_type_times_2500_plus_width_times_height_times_1800
           xcf_file_size_mod_229_times_15_plus_image_type_times_750_plus_layer_count_times_2500
"""
from pathlib import Path
import sys

_REPO = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.xcf import (
    xcf_file_size_mod_227_times_12_plus_image_type_times_2500_plus_width_times_height_times_1800,
    xcf_file_size_mod_229_times_15_plus_image_type_times_750_plus_layer_count_times_2500,
)

SAMPLES = _REPO / "samples/by-format/xcf/valid"
BLUE = SAMPLES / "1x1-rgba-blue.xcf"
RED = SAMPLES / "1x1-red-rgb.xcf"
GRAY = SAMPLES / "2x2-gray.xcf"


class TestXcfMod227F1:
    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_227_times_12_plus_image_type_times_2500_plus_width_times_height_times_1800(BLUE), int)

    def test_blue_expected_value(self):
        assert xcf_file_size_mod_227_times_12_plus_image_type_times_2500_plus_width_times_height_times_1800(BLUE) == 3936

    def test_red_expected_value(self):
        assert xcf_file_size_mod_227_times_12_plus_image_type_times_2500_plus_width_times_height_times_1800(RED) == 3924

    def test_gray_expected_value(self):
        assert xcf_file_size_mod_227_times_12_plus_image_type_times_2500_plus_width_times_height_times_1800(GRAY) == 11836

    def test_returns_nonnegative(self):
        assert xcf_file_size_mod_227_times_12_plus_image_type_times_2500_plus_width_times_height_times_1800(BLUE) >= 0

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_227_times_12_plus_image_type_times_2500_plus_width_times_height_times_1800(Path(BLUE))
        assert isinstance(result, int)


class TestXcfMod229F2:
    def test_blue_returns_int(self):
        assert isinstance(xcf_file_size_mod_229_times_15_plus_image_type_times_750_plus_layer_count_times_2500(BLUE), int)

    def test_blue_expected_value(self):
        assert xcf_file_size_mod_229_times_15_plus_image_type_times_750_plus_layer_count_times_2500(BLUE) == 5170

    def test_red_expected_value(self):
        assert xcf_file_size_mod_229_times_15_plus_image_type_times_750_plus_layer_count_times_2500(RED) == 5155

    def test_gray_expected_value(self):
        assert xcf_file_size_mod_229_times_15_plus_image_type_times_750_plus_layer_count_times_2500(GRAY) == 5920

    def test_returns_nonnegative(self):
        assert xcf_file_size_mod_229_times_15_plus_image_type_times_750_plus_layer_count_times_2500(BLUE) >= 0

    def test_accepts_path_object(self):
        result = xcf_file_size_mod_229_times_15_plus_image_type_times_750_plus_layer_count_times_2500(Path(BLUE))
        assert isinstance(result, int)
